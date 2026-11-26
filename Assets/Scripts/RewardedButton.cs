using UnityEngine;

/// <summary>
/// 商店里的「看广告领奖励」按钮，统一走抖音小游戏广告链路 AdManager。
/// 看完广告必定发放 rewardAmount 宝石（编辑器下直接发放，方便调试）。
/// </summary>
public class RewardedButton : MonoBehaviour
{
	public GameObject content;

	[Tooltip("看完激励视频奖励的货币数量")]
	public int rewardAmount = 50;

	public void OnClick()
	{
		if (AdManager.Instance == null)
		{
			Debug.LogWarning("[RewardedButton] 场景中没有 AdManager，无法播放激励视频");
			return;
		}

		Sound.instance.PlayButton();

#if UNITY_EDITOR
		// 编辑器里 TTSDK 是 mock，直接发奖方便调试
		Debug.Log("[RewardedButton] 编辑器模式：跳过广告播放，直接发放奖励");
		OnAdWatched();
#else
		AdManager.Instance.ShowRewardedVideoAd(OnAdWatched, OnAdFailed);
#endif
	}

	private void OnAdWatched()
	{
		int amount = rewardAmount > 0 ? rewardAmount : 50;
		CurrencyController.CreditBalance(amount);

		if (content != null)
		{
			// content 是按钮上的「＋」图标，领过就隐藏
			content.SetActive(value: false);
		}

		if (Toast.instance != null)
		{
			Toast.instance.ShowMessage($"获得 {amount} 宝石");
		}

		Debug.Log($"[RewardedButton] 奖励已发放：{amount} 宝石，当前余额 {CurrencyController.GetBalance()}");
	}

	private void OnAdFailed(string message)
	{
		Debug.LogWarning("[RewardedButton] 激励视频未完成：" + message);
		if (Toast.instance != null && !string.IsNullOrEmpty(message))
		{
			Toast.instance.ShowMessage(message);
		}
	}
}
