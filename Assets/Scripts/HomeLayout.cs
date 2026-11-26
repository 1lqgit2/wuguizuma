using UnityEngine;

/// <summary>
/// Home（标题页）布局自适应。
///
/// 这个场景的 UI 是按旧版横屏画布（1256×699）手工摆的，换成抖音小游戏后：
/// - Background 固定 1256×699，屏幕比例一变就上下/左右露底（启动画面只剩中间一条带）；
/// - ButtonPlay 的 anchoredPosition.y = -464 相对"顶部"锚点，画布一变成 640 高就整颗跑出屏幕；
/// - 音乐/音效按钮的 x 是 -870，整组都在屏幕左侧外面；
/// - Privacy/More 用的是 480 的原始尺寸 + 0.455 缩放，在 640 高的画布上偏大且贴出下边缘。
///
/// 挂到 Canvas 上即可。Start 后按画布实际尺寸重排，屏幕尺寸/朝向变化会自动重排。
/// 只改位置与整体缩放，不动贴图、Spine 动画和交互；标题木牌保持原样。
/// </summary>
[DisallowMultipleComponent]
public class HomeLayout : MonoBehaviour
{
	[Header("底板")]
	[Tooltip("底板的原始设计尺寸，用来做等比放大铺满（保持宽高比，不拉伸）")]
	public Vector2 backgroundDesignSize = new Vector2(1256f, 699f);

	[Header("比例（相对画布高度 h）")]
	[Tooltip("开始按钮显示高度")]
	[Range(0.05f, 0.3f)] public float playHeight = 0.15f;

	[Tooltip("开始按钮距屏幕底部的距离")]
	[Range(0f, 0.3f)] public float playBottom = 0.045f;

	[Tooltip("右侧音乐/音效按钮显示高度")]
	[Range(0.05f, 0.3f)] public float sideButtonHeight = 0.16f;

	[Tooltip("左右下角 Privacy / More 显示高度")]
	[Range(0.05f, 0.3f)] public float cornerButtonHeight = 0.18f;

	[Tooltip("左右下角留边")]
	[Range(0f, 0.2f)] public float cornerMargin = 0.05f;

	private RectTransform canvasRect;
	private Vector2 lastSize;

	private void Start()
	{
		canvasRect = transform as RectTransform;
		Apply();
	}

	private void LateUpdate()
	{
		// 分辨率/朝向变化时重新排一次（抖音小游戏切前后台、真机横竖屏切换都会改尺寸）
		if (canvasRect == null)
		{
			canvasRect = transform as RectTransform;
			if (canvasRect == null)
				return;
		}

		Vector2 size = canvasRect.rect.size;
		if (size != lastSize && size.x > 1f && size.y > 1f)
		{
			Apply();
		}
	}

	public void Apply()
	{
		if (canvasRect == null)
			canvasRect = transform as RectTransform;
		if (canvasRect == null)
			return;

		float w = canvasRect.rect.width;
		float h = canvasRect.rect.height;
		if (w <= 1f || h <= 1f)
			return; // 画布还没算好尺寸，等下一帧

		lastSize = new Vector2(w, h);

		CoverBackground(w, h);

		// 开始按钮：底部居中。标题木牌保持原位，按钮压在木牌下沿一点点，视觉上是"牌子下面的按钮"
		RectTransform play = Find("ButtonPlay");
		if (play != null)
		{
			SetHeight(play, h * playHeight);
			Place(play, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, h * playBottom));
		}

		// 右侧音乐/音效按钮：竖直排在右边，留出安全边距
		RectTransform buttons = Find("Buttons");
		if (buttons != null)
		{
			Place(buttons, new Vector2(1f, 0.5f), new Vector2(0.5f, 0.5f),
				new Vector2(-w * 0.06f, 0f));

			RectTransform music = Find("ToggleButtonMusic", buttons);
			RectTransform sound = Find("ToggleButtonSound", buttons);

			SetHeight(music, h * sideButtonHeight);
			SetHeight(sound, h * sideButtonHeight);

			Place(music, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0f, h * sideButtonHeight * 0.62f));
			Place(sound, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0f, -h * sideButtonHeight * 0.62f));
		}

		// 左下 / 右下 的胶囊按钮
		SetCorner(Find("Privacy"), new Vector2(0f, 0f), h);
		SetCorner(Find("More"), new Vector2(1f, 0f), h);

		LogLayout(w, h, play, buttons);
	}

	/// <summary>底板等比放大到完全盖住屏幕，避免露出相机底色</summary>
	private void CoverBackground(float w, float h)
	{
		RectTransform bg = Find("Background");
		if (bg == null)
			return;

		float designW = Mathf.Max(1f, backgroundDesignSize.x);
		float designH = Mathf.Max(1f, backgroundDesignSize.y);
		float scale = Mathf.Max(w / designW, h / designH);

		bg.anchorMin = bg.anchorMax = new Vector2(0.5f, 0.5f);
		bg.pivot = new Vector2(0.5f, 0.5f);
		bg.anchoredPosition = Vector2.zero;
		bg.sizeDelta = new Vector2(designW * scale, designH * scale);
	}

	/// <summary>按目标显示高度等比缩放（只动 localScale，不动 sizeDelta 里的原始数值）</summary>
	private static void SetHeight(RectTransform rt, float targetHeight)
	{
		if (rt == null)
			return;

		float baseHeight = rt.rect.size.y;
		if (baseHeight <= 1f)
			return;

		float k = targetHeight / baseHeight;
		rt.localScale = new Vector3(k, k, 1f);
	}

	/// <summary>角落按钮：缩放后贴角摆放，保证整颗都在屏幕内</summary>
	private void SetCorner(RectTransform rt, Vector2 anchor, float h)
	{
		if (rt == null)
			return;

		float target = h * cornerButtonHeight;
		SetHeight(rt, target);

		float half = target * 0.5f;
		float margin = h * cornerMargin;

		// anchor 取的是左下角/右下角，anchoredPosition 相对该角，直接给正数偏移
		float x = ((anchor.x < 0.5f) ? 1f : -1f) * (margin + half);
		float y = margin + half;

		Place(rt, anchor, new Vector2(0.5f, 0.5f), new Vector2(x, y));
	}

	private static void Place(RectTransform rt, Vector2 anchor, Vector2 pivot, Vector2 anchoredPos)
	{
		if (rt == null)
			return;

		rt.anchorMin = anchor;
		rt.anchorMax = anchor;
		rt.pivot = pivot;
		rt.anchoredPosition = anchoredPos;
	}

	private RectTransform Find(string name, Transform parent = null)
	{
		Transform root = parent != null ? parent : transform;
		Transform child = root.Find(name);
		if (child != null)
			return child as RectTransform;

		// 有些版本节点被塞进了子层级，兜底再找一次
		Transform deep = FindDeep(root, name);
		return deep as RectTransform;
	}

	private static Transform FindDeep(Transform root, string name)
	{
		for (int i = 0; i < root.childCount; i++)
		{
			Transform c = root.GetChild(i);
			if (c.name == name)
				return c;
			Transform r = FindDeep(c, name);
			if (r != null)
				return r;
		}
		return null;
	}

	private void LogLayout(float w, float h, RectTransform play, RectTransform buttons)
	{
#if UNITY_EDITOR
		Debug.Log("[主页布局] 画布 " + w.ToString("F0") + "x" + h.ToString("F0")
			+ "  开始按钮=" + Describe(play)
			+ "  侧栏=" + Describe(buttons));
#endif
	}

	private static string Describe(RectTransform rt)
	{
		if (rt == null)
			return "未找到";

		return "(" + rt.anchoredPosition.x.ToString("F0") + "," + rt.anchoredPosition.y.ToString("F0")
			+ ") 高" + (rt.rect.size.y * rt.localScale.y).ToString("F0");
	}
}
