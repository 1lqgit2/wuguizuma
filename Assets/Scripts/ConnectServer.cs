using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class ConnectServer : MonoBehaviour
{
	protected delegate void OnGetDataSuccess(string data);

	[Tooltip("Example: https://superpow.herokuapp.com/legend/")]
	public string rootUrl;

	[Tooltip("Example: 1.0")]
	public string versionAPI;

	[Tooltip("Request timeout in seconds.")]
	public int requestTimeout = 10;

	[Tooltip("Print a warning when a request fails. Turn off to keep the console clean while offline.")]
	public bool logRequestErrors = true;

	[Tooltip("抖音小游戏只允许 https + 后台白名单域名，http 请求在真机/开发者工具里必定失败（url use invalid protocol）。开启后打包版本直接跳过非 https 请求。")]
	public bool skipInsecureRequestsInBuild = true;

	protected IEnumerator GetDataFromServer(string url, OnGetDataSuccess onGetDataSuccess)
	{
		// 平台限制：非 https 的地址在抖音小游戏里一定报错，跳过，避免控制台刷屏
		if (skipInsecureRequestsInBuild && !Application.isEditor &&
			!string.IsNullOrEmpty(url) &&
			!url.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
		{
			yield break;
		}

		if (string.IsNullOrEmpty(url) || !Uri.IsWellFormedUriString(url, UriKind.Absolute))
		{
			Warn("Invalid url, request skipped: " + url);
			yield break;
		}

		UnityWebRequest request;
		string startError;
		if (!TryStartRequest(url, requestTimeout, out request, out startError))
		{
			Warn("Request rejected (" + url + "): " + startError +
				"\nIf this is a http:// address either allow it in Player Settings > Allow downloads over HTTP, or switch the address to https://.");
			yield break;
		}

		yield return request;

		bool success = request.result == UnityWebRequest.Result.Success;
		string text = success ? request.downloadHandler.text : null;
		string error = request.error;
		long responseCode = request.responseCode;
		request.Dispose();

		if (!success)
		{
			Warn("GetDataFromServer failed (" + url + "): " + error + " [HTTP " + responseCode + "]");
			yield break;
		}

		if (!string.IsNullOrEmpty(text) && onGetDataSuccess != null)
		{
			onGetDataSuccess(text);
		}
	}

	// SendWebRequest throws synchronously when Unity refuses the connection
	// (e.g. plain http while "Allow downloads over HTTP" is disabled). The call is
	// kept inside a plain method so the coroutine never has to yield across a try/catch.
	private static bool TryStartRequest(string url, int timeout, out UnityWebRequest request, out string error)
	{
		request = null;
		error = null;

		try
		{
			request = UnityWebRequest.Get(url);
			request.timeout = timeout;
			request.SendWebRequest();
			return true;
		}
		catch (Exception e)
		{
			error = e.Message;
			if (request != null)
			{
				request.Dispose();
				request = null;
			}
			return false;
		}
	}

	private void Warn(string message)
	{
		if (logRequestErrors)
		{
			UnityEngine.Debug.LogWarning("[ConnectServer] " + message);
		}
	}
}
