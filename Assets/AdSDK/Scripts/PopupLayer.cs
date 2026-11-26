using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>
/// 弹窗宿主。
///
/// 之前的做法是运行时 new 一个常驻 Overlay 画布（PopupCanvas）再往上挂，
/// 结果弹窗被 SetActive 了、日志也打印了父级，但屏幕上始终看不到东西
/// ——运行期新建的画布在部分场景组合下会出现"有 rect、不渲染"的情况，
/// 排查成本非常高。
///
/// 现在改成：优先直接挂到场景里正在使用的 UI 画布（MainUI）。
/// 那个画布上的地图、底栏、按钮都能正常显示和点击，弹窗挂上去就一定能渲染，
/// 缩放、参考分辨率、CanvasRefiner 的虚拟分辨率也天然一致。
/// 只有在场景里完全找不到可用画布时，才退回到自建的常驻 Overlay 画布。
/// </summary>
public static class PopupLayer
{
    private const int SortingOrder = 100;
    private static Canvas canvas;

    /// <summary>弹窗应挂载的父节点。优先场景画布，找不到才自建。</summary>
    public static Transform Get()
    {
        Transform sceneRoot = FindSceneCanvasRoot();
        if (sceneRoot != null)
            return sceneRoot;

        return GetStandaloneCanvas();
    }

    /// <summary>自建的常驻 Overlay 画布（兜底用）。</summary>
    public static Transform GetStandaloneCanvas()
    {
        if (canvas != null)
            return canvas.transform;

        GameObject found = GameObject.Find("PopupCanvas");
        if (found != null)
        {
            canvas = found.GetComponent<Canvas>();
            if (canvas != null)
                return canvas.transform;
        }

        GameObject go = new GameObject("PopupCanvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        canvas = go.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = SortingOrder;
        canvas.enabled = true;
        go.layer = 5; // UI

        CanvasScaler scaler = go.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(640f, 1136f);
        scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;

        Object.DontDestroyOnLoad(go);
        Debug.Log("[UI] 场景里没有可用画布，已创建兜底弹窗画布 PopupCanvas（Overlay, sortingOrder=" + SortingOrder + "）");
        return canvas.transform;
    }

    /// <summary>把宿主画布的关键状态打成一行日志，方便确认到底挂在哪个画布上。</summary>
    public static string Describe(Transform host)
    {
        if (host == null)
            return "无";

        Canvas c = host.GetComponent<Canvas>();
        if (c == null)
            c = host.GetComponentInParent<Canvas>();
        if (c == null)
            return host.name + "（无 Canvas 组件）";

        RectTransform rt = c.transform as RectTransform;
        return string.Format("{0} mode={1} order={2} enabled={3} scale={4:0.###} rect={5}",
            c.name, c.renderMode, c.sortingOrder, c.enabled, c.scaleFactor, rt != null ? rt.rect.size.ToString() : "?");
    }

    /// <summary>
    /// 找场景里正在使用的 UI 画布。
    /// 先按名字找 MainUI（Map / Home 的主界面画布），
    /// 找不到再取当前场景里第一个非 WorldSpace 的根画布。
    /// 注意要排除 DontDestroyOnLoad 里的常驻画布，那是 GameMaster 的 Toast/转场层。
    /// </summary>
    private static Transform FindSceneCanvasRoot()
    {
        GameObject main = GameObject.Find("MainUI");
        if (main != null)
        {
            Canvas mainCanvas = main.GetComponent<Canvas>();
            if (mainCanvas != null && mainCanvas.isActiveAndEnabled)
                return mainCanvas.transform;
        }

        Scene active = SceneManager.GetActiveScene();
        Canvas[] all = Object.FindObjectsOfType<Canvas>();
        for (int i = 0; i < all.Length; i++)
        {
            Canvas c = all[i];
            if (c == null || !c.isActiveAndEnabled)
                continue;
            if (!c.isRootCanvas || c.renderMode == RenderMode.WorldSpace)
                continue;
            if (c.gameObject.scene != active)
                continue;
            return c.transform;
        }

        return null;
    }
}
