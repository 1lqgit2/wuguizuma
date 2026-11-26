using System;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 激励广告确认弹窗（jiliBtn「看广告领奖励」打开的面板）。
/// 打开方式有两种：
/// 1) AdConfirm.Show(callback) —— 外部指定奖励逻辑；
/// 2) 直接 SetActive(true)（场景里 jiliBtn 的 onClick 就是这么接的）——
///    此时没有外部回调，OnEnable 会自动挂上默认奖励，保证看完广告一定发奖。
/// </summary>
public class AdConfirm : MonoBehaviour
{
    private static AdConfirm instance;

    [SerializeField] private Button btnClose;
    [SerializeField] private Button btnConfirm;

    [Header("默认奖励（没有外部回调时发放的宝石数量）")]
    [SerializeField] private int defaultRewardAmount = 50;

    private Action onCompleted;

    /// <summary>广告播放中，防止连点重复拉起</summary>
    private bool adPlaying;

    /// <summary>
    /// 给场景按钮（jiliBtn）用的入口：优先复用场景里已有的 AdConfirm 实例，
    /// 没有才从 Resources 新建。这样即使 Inspector 上的 onClick 丢失，按钮仍然能打开面板。
    /// </summary>
    public static void OpenFromButton()
    {
        AdConfirm existing = FindObjectOfType<AdConfirm>(true);
        if (existing != null)
        {
            instance = existing;

            if (!existing.gameObject.activeSelf)
            {
                // 新的一次打开：先清掉上一次可能残留的临时回调，OnEnable 会重新挂默认奖励
                existing.onCompleted = null;
                existing.gameObject.SetActive(true);
            }
            else if (existing.onCompleted == null)
            {
                // 关键：场景里按钮原本的 onClick（SetActive）会先执行，OnEnable 已经跑过一次、
                // 把默认奖励挂上了。这里如果无脑 onCompleted = null，就会把刚挂好的回调抹掉，
                // 而对象已经激活、OnEnable 不会再跑 —— 结果就是"点确定只关面板、不发奖"。
                existing.onCompleted = existing.GrantDefaultReward;
                Debug.Log("[广告] AdConfirm 已处于打开状态，补挂默认奖励回调");
            }

            existing.NormalizeRect();
            existing.MoveToRootCanvas();
            Debug.Log("[广告] jiliBtn → 打开场景里的 AdConfirm 实例");
            return;
        }

        Show(null);
        Debug.Log("[广告] jiliBtn → 场景里没有 AdConfirm 实例，已从 Resources 新建");
    }

    public static void Show(Action callBack)
    {
        if (instance == null)
        {
            // 加载 AdConfirm 预制体
            GameObject prefab = Resources.Load<GameObject>("AdConfirm");
            if (prefab == null)
            {
                Debug.LogError("AdConfirm 预制体未找到，请确保其位于 Resources 文件夹中。");
                return;
            }

            // 实例化 AdConfirm（挂在主 Canvas 下，预制体本身不再带 Canvas）
            Transform canvasRoot = GetRootCanvasTransform();
            GameObject adConfirmInstance = canvasRoot != null
                ? Instantiate(prefab, canvasRoot, false)
                : Instantiate(prefab);
            instance = adConfirmInstance.GetComponent<AdConfirm>();

            if (instance == null)
            {
                Debug.LogError("AdConfirm 脚本未附加到预制体上，请检查预制体设置。");
                Destroy(adConfirmInstance);
                return;
            }
        }

        // 设置回调并显示弹窗
        instance.onCompleted = callBack;
        instance.transform.SetAsLastSibling();
        instance.gameObject.SetActive(true);
    }

    private static Transform GetRootCanvasTransform()
    {
        // 统一挂到最上层的弹窗画布，避免被 GameMaster 的常驻 Overlay 画布盖住
        return PopupLayer.Get();
    }

    private void OnEnable()
    {
        // 场景里旧版本残留过旋转 90°、anchor/size 被覆盖的 RectTransform，
        // 显隐一次就会把弹窗丢到屏幕外或缩成 0，这里强制纠正一次。
        NormalizeRect();
        // 父节点如果还是老的 Footer（100x100），重新挂回场景主画布并置顶
        MoveToRootCanvas();
        // 场景里的实例有可能是空壳（预制体被改过、子节点断链），这种情况直接重建
        EnsureHasChildren();

        adPlaying = false;
        SetConfirmInteractable(true);

        // 没有外部回调（场景里直接用 SetActive 打开的情况）时，挂默认奖励
        if (onCompleted == null)
        {
            onCompleted = GrantDefaultReward;
        }

        RectTransform rt = transform as RectTransform;
        Debug.Log($"[广告] AdConfirm 已打开 父级={(transform.parent ? transform.parent.name : "无")} "
                  + $"rect={(rt ? rt.rect.size.ToString() : "null")} "
                  + $"子节点={transform.childCount} 图形={GetComponentsInChildren<Graphic>(true).Length} "
                  + $"世界缩放={transform.lossyScale} active={gameObject.activeInHierarchy}");
        Debug.Log("[广告] 宿主画布：" + PopupLayer.Describe(transform.parent));
        LogScreenRect();
    }

    private void Awake()
    {
        // 之前这里是 Destroy(gameObject)：只要有第二个实例（例如别处调过 Show()），
        // 场景里这个实例一被 SetActive 就会把自己删掉，表现就是"点了没反应"。
        // 改成后来者接管：旧的收起，新的生效。
        if (instance != null && instance != this && instance.gameObject != null)
        {
            instance.gameObject.SetActive(false);
        }

        instance = this;

        // 根节点残留 Mask / RectMask2D 会把整棵子树裁掉：表现为"看不见但挡点击"
        Mask stencilMask = GetComponent<Mask>();
        if (stencilMask != null)
        {
            Destroy(stencilMask);
            Debug.LogWarning("[广告] AdConfirm 根节点残留 Mask，已移除");
        }
        RectMask2D rectMask = GetComponent<RectMask2D>();
        if (rectMask != null)
        {
            rectMask.enabled = false;
        }

        btnClose?.onClick.AddListener(this.OnClose);
        btnConfirm?.onClick.AddListener(this.OnConfirm);
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

        // 无条件回正：锚点/缩放/旋转/z 任何一项被改过，都会让弹窗"屏幕上看不见、但点击照样挡住"
        // （localPosition.z 跑到相机裁剪面外时，WorldToScreenPoint 仍返回满屏坐标，日志看着完全正常）
        rt.localScale = Vector3.one;
        rt.localRotation = Quaternion.identity;
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;
        rt.anchoredPosition3D = Vector3.zero;

        if (broken)
        {
            Debug.LogWarning("[广告] AdConfirm 根节点布局被改坏了，已重置为全屏 stretch");
        }
    }

    /// <summary>
    /// 挂到场景里正在使用的 UI 画布（MainUI）。
    /// 之前挂的是运行时自建的 PopupCanvas，那个画布在部分情况下不渲染，
    /// 表现就是"日志说已打开，屏幕上什么都没有"。挂回场景画布后与地图/底栏同一渲染链路。
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
            Debug.Log("[广告] AdConfirm 已从 " + oldParentName + " 改挂到 " + root.name);
        }
        transform.SetAsLastSibling();
    }

    /// <summary>把弹窗根节点的屏幕范围打出来，用来确认它到底有没有落在可见区域内。</summary>
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
        Debug.Log($"[广告] 屏幕范围 min={min} max={max} Screen={Screen.width}x{Screen.height} camera={(cam != null ? cam.name : "null")}");
    }

    /// <summary>
    /// 场景里的预制体实例如果子节点丢了（预制体结构被改过、覆盖数据错乱），
    /// 激活之后就是一个全屏空壳：rect 正常、父级正常，但屏幕上什么都没有。
    /// 这里检测到 0 个子节点就用 Resources 里的预制体重建一份。
    /// </summary>
    private void EnsureHasChildren()
    {
        if (transform.childCount > 0)
            return;

        GameObject prefab = Resources.Load<GameObject>("AdConfirm");
        if (prefab == null)
        {
            Debug.LogError("[广告] AdConfirm 实例没有任何子节点，且 Resources 里找不到 AdConfirm 预制体");
            return;
        }

        GameObject fresh = Instantiate(prefab); // 先在根上实例化，Awake 里会接管 instance
        if (fresh.transform.parent == null)
            fresh.transform.SetParent(transform.parent, false);
        fresh.name = name + "(rebuild)";
        Debug.LogWarning("[广告] 场景里的 AdConfirm 是空壳（0 个子节点），已用预制体重建一份");
        gameObject.SetActive(false);
    }

    private void OnClose()
    {
        adPlaying = false;
        SetConfirmInteractable(true);
        // 关闭时清空回调，避免下次被复用到旧奖励
        onCompleted = null;
        gameObject.SetActive(false);
    }

    private void OnConfirm()
    {
        if (adPlaying)
        {
            Debug.Log("[广告] 激励视频正在播放，忽略重复点击");
            return;
        }

        adPlaying = true;
        SetConfirmInteractable(false);

#if UNITY_EDITOR
        // 编辑器里 TTSDK 是 mock，直接发奖方便调试
        Debug.Log("[广告] 编辑器模式：跳过广告播放，直接发放奖励");
        FinishAd();
#else
        if (AdManager.Instance == null)
        {
            Debug.LogError("[广告] 场景里没有 AdManager，无法播放广告");
            OnAdError("广告服务未初始化");
            return;
        }
        AdManager.Instance.ShowRewardedVideoAd(OnAdWatched, OnAdError);
#endif
    }

    private void OnAdWatched()
    {
        Debug.Log("[广告] 激励视频观看完成，发放奖励");
        FinishAd();
    }

    /// <summary>看完广告后统一走这里：发奖励 + 关闭面板</summary>
    private void FinishAd()
    {
        adPlaying = false;
        SetConfirmInteractable(true);

        var callback = onCompleted;
        onCompleted = null;

        // 兜底：任何路径下都不允许"看完广告什么都没发"。
        // 之前 OpenFromButton 会把 OnEnable 刚挂的默认奖励清空，导致这里 callback == null，
        // 表现就是面板被关掉、宝石没增加。
        if (callback == null)
        {
            Debug.LogWarning("[广告] 没有外部奖励回调，改发默认奖励");
            callback = GrantDefaultReward;
        }

        callback();

        OnClose();
    }

    private void GrantDefaultReward()
    {
        if (defaultRewardAmount <= 0)
        {
            Debug.LogWarning("[广告] 默认奖励数量为 0，请检查 AdConfirm 预制体上的 defaultRewardAmount");
            return;
        }

        CurrencyController.CreditBalance(defaultRewardAmount);
        if (Toast.instance != null)
        {
            Toast.instance.ShowMessage($"获得 {defaultRewardAmount} 宝石");
        }
        Debug.Log($"[广告] 激励奖励已发放：{defaultRewardAmount} 宝石，当前余额 {CurrencyController.GetBalance()}");
    }

    private void SetConfirmInteractable(bool value)
    {
        if (btnConfirm != null)
        {
            btnConfirm.interactable = value;
        }
    }

    private void OnAdError(string errorMessage)
    {
        adPlaying = false;
        SetConfirmInteractable(true);
        Debug.LogError($"广告播放失败: {errorMessage}");

        // 加载 AdError 预制体
        GameObject adErrorPrefab = Resources.Load<GameObject>("AdError");
        if (adErrorPrefab != null)
        {
            // 实例化 AdError
            GameObject adErrorInstance = Instantiate(adErrorPrefab, transform.position, Quaternion.identity);
            // 1 秒后销毁实例
            Destroy(adErrorInstance, 1.5f);
        }
        else
        {
            Debug.LogError("AdError 预制体未找到，请确保其位于 Resources 文件夹中。");
        }
    }
}
