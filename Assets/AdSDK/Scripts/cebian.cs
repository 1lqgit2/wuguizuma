using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TTSDK;
using TTSDK.UNBridgeLib.LitJson;

public class cebian : MonoBehaviour
{
    //前往按钮
    public Button btn_Go;

    /// <summary>
    /// 给场景按钮（cebianBtn）用的入口：优先复用场景里已有的面板实例，
    /// 没有才从 Resources 新建。即使 Inspector 上的 onClick 丢了也点得开。
    /// </summary>
    public static void OpenPanel()
    {
        cebian existing = FindObjectOfType<cebian>(true);
        if (existing != null)
        {
            if (!existing.gameObject.activeSelf)
                existing.gameObject.SetActive(true);

            existing.NormalizeRect();
            existing.MoveToRootCanvas();
            Debug.Log("[侧边栏] cebianBtn → 打开场景里的 cebianPanel 实例");
            return;
        }

        GameObject prefab = Resources.Load<GameObject>("cebianPanel");
        if (prefab == null)
        {
            Debug.LogError("[侧边栏] cebianPanel 预制体未找到（应在 Assets/AdSDK/Resources 下）");
            return;
        }

        GameObject go = Instantiate(prefab, PopupLayer.Get(), false);
        go.SetActive(true);
        Debug.Log("[侧边栏] cebianBtn → 场景里没有实例，已从 Resources 新建");
    }

    private void Awake()
    {
        // 场景里该面板是常驻但隐藏的，按钮事件在 Awake 里挂一次即可，避免多次显隐重复注册
        if (btn_Go != null)
        {
            btn_Go.onClick.RemoveListener(NavigateToSideBar);
            btn_Go.onClick.AddListener(NavigateToSideBar);
        }

        // 根节点上只要残留 Mask / RectMask2D，就会把整棵子树裁掉：
        // 表现出来就是"面板看不见，但整屏点击都被它吃掉"
        Mask stencilMask = GetComponent<Mask>();
        if (stencilMask != null)
        {
            Destroy(stencilMask);
            Debug.LogWarning("[侧边栏] 根节点残留 Mask（会把面板整棵子树裁掉），已移除");
        }
        RectMask2D rectMask = GetComponent<RectMask2D>();
        if (rectMask != null)
        {
            rectMask.enabled = false;
        }

        EnsureClickOutsideToClose();
    }

    /// <summary>点面板外面（半透明黑底）就关掉，避免"打开后其他按钮全点不动"。</summary>
    private void EnsureClickOutsideToClose()
    {
        Button btn = GetComponent<Button>();
        if (btn == null)
        {
            btn = gameObject.AddComponent<Button>();
        }
        btn.transition = Selectable.Transition.None;
        btn.onClick.RemoveListener(OnBackgroundClicked);
        btn.onClick.AddListener(OnBackgroundClicked);
    }

    private void OnBackgroundClicked()
    {
        Transform box = transform.Find("box");
        if (box != null)
        {
            Canvas cv = GetComponentInParent<Canvas>();
            Camera cam = (cv != null && cv.renderMode != RenderMode.ScreenSpaceOverlay) ? cv.worldCamera : null;
            if (RectTransformUtility.RectangleContainsScreenPoint((RectTransform)box, Input.mousePosition, cam))
            {
                return; // 点在面板本体上，不关闭
            }
        }
        gameObject.SetActive(false);
    }

    private void OnEnable()
    {
        NormalizeRect();
        MoveToRootCanvas();
        EnsureHasChildren();

        RectTransform rt = transform as RectTransform;
        Debug.Log($"[侧边栏] cebianPanel 已打开 父级={(transform.parent ? transform.parent.name : "无")} "
                  + $"rect={(rt ? rt.rect.size.ToString() : "null")} "
                  + $"子节点={transform.childCount} 图形={GetComponentsInChildren<Graphic>(true).Length} "
                  + $"世界缩放={transform.lossyScale} active={gameObject.activeInHierarchy}");
        Debug.Log("[侧边栏] 宿主画布：" + PopupLayer.Describe(transform.parent));
        LogScreenRect();

#if UNITY_EDITOR
        Transform box = transform.Find("box");
        if (box != null)
        {
            Graphic g = box.GetComponent<Graphic>();
            if (g != null && g.canvasRenderer != null)
            {
                Debug.Log($"[侧边栏] box 渲染状态 cull={g.canvasRenderer.cull} "
                          + $"rendererAlpha={g.canvasRenderer.GetAlpha():F2} colorAlpha={g.color.a:F2} "
                          + $"active={g.gameObject.activeInHierarchy} rect={((RectTransform)box).rect.size}");
            }
        }
#endif
    }

    /// <summary>把面板根节点的屏幕范围打出来，用来确认它到底有没有落在可见区域内。</summary>
    private void LogScreenRect()
    {
        RectTransform rt = transform as RectTransform;
        if (rt == null)
            return;

        Canvas hostCanvas = GetComponentInParent<Canvas>();
        Camera cam = (hostCanvas != null && hostCanvas.renderMode == RenderMode.ScreenSpaceCamera) ? hostCanvas.worldCamera : null;

        Vector3[] corners = new Vector3[4];
        rt.GetWorldCorners(corners);
        Vector2 min = RectTransformUtility.WorldToScreenPoint(cam, corners[0]);
        Vector2 max = RectTransformUtility.WorldToScreenPoint(cam, corners[2]);
        Debug.Log($"[侧边栏] 屏幕范围 min={min} max={max} Screen={Screen.width}x{Screen.height} camera={(cam != null ? cam.name : "null")}");
    }

    /// <summary>把根节点的 RectTransform 拉回"全屏 stretch、不缩放不旋转"</summary>
    private void NormalizeRect()
    {
        RectTransform rt = transform as RectTransform;
        if (rt == null)
            return;

        bool broken = rt.localScale != Vector3.one
                      || Quaternion.Angle(rt.localRotation, Quaternion.identity) > 0.5f
                      || rt.anchorMin != Vector2.zero
                      || rt.anchorMax != Vector2.one
                      || rt.offsetMin != Vector2.zero
                      || rt.offsetMax != Vector2.zero
                      || Mathf.Abs(rt.localPosition.z) > 0.01f;

        // 无条件回正：锚点/缩放/旋转/z 任何一项被改过，都会让面板"屏幕上看不见、但点击照样挡住"
        // （localPosition.z 跑到相机裁剪面外时，WorldToScreenPoint 仍会返回满屏坐标，日志看着完全正常）
        rt.localScale = Vector3.one;
        rt.localRotation = Quaternion.identity;
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;
        rt.anchoredPosition3D = Vector3.zero;

        if (broken)
        {
            Debug.LogWarning("[侧边栏] cebianPanel 根节点布局被改坏了，已重置为全屏 stretch");
        }
    }

    /// <summary>
    /// 挂到场景里正在使用的 UI 画布（MainUI），与地图/底栏同一条渲染链路。
    /// 之前挂的运行时自建 PopupCanvas 会出现"有 rect 但不渲染"的问题。
    /// </summary>
    private void MoveToRootCanvas()
    {
        Transform root = PopupLayer.Get();
        if (root == null)
            return;

        if (transform.parent != root)
        {
            string oldParentName = transform.parent != null ? transform.parent.name : "无";
            transform.SetParent(root, false);
            Debug.Log("[侧边栏] cebianPanel 已从 " + oldParentName + " 改挂到 " + root.name);
        }
        transform.SetAsLastSibling();
    }

    /// <summary>
    /// 场景实例如果是空壳（预制体被改过，子节点断链），激活后就是一个全屏空面板，
    /// 日志说打开了但屏幕上看不到内容。检测到 0 个子节点就用预制体重建一份。
    /// </summary>
    private void EnsureHasChildren()
    {
        if (transform.childCount > 0)
            return;

        GameObject prefab = Resources.Load<GameObject>("cebianPanel");
        if (prefab == null)
        {
            Debug.LogError("[侧边栏] cebianPanel 实例没有任何子节点，且 Resources 里找不到预制体");
            return;
        }

        GameObject fresh = Instantiate(prefab);
        if (fresh.transform.parent == null)
            fresh.transform.SetParent(transform.parent, false);
        fresh.name = name + "(rebuild)";
        fresh.SetActive(true);
        Debug.LogWarning("[侧边栏] 场景里的 cebianPanel 是空壳（0 个子节点），已用预制体重建一份");
        gameObject.SetActive(false);
    }

    private void Start()
    {
        //检查是否支持侧边栏功能
        //CheckSideBarSupport();
        if (btn_Go == null)
        {
            Debug.LogWarning("[侧边栏] btn_Go 未绑定，前往侧边栏按钮不会响应");
        }
    }

    /// <summary>
    /// 跳转到侧边栏
    /// </summary>
    public void NavigateToSideBar()
    {
        try
        {
            var data = new JsonData
            {
                ["scene"] = "sidebar",
            };
            TT.NavigateToScene(data, () =>
            {
                Debug.Log("navigate to scene success");
            }, () =>
            {
                Debug.Log("navigate to scene complete");
            }, (errCode, errMsg) =>
            {
                Debug.Log($"navigate to scene error, errCode:{errCode}, errMsg:{errMsg}");
            });
        }
        catch (System.Exception e)
        {
            Debug.LogError("跳转到侧边栏异常: " + e.Message);
        }
    }
}
