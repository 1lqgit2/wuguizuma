using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>
/// 场景里 cebianBtn / jiliBtn 的兜底绑定。
/// 这两个按钮原本靠 Inspector 上的 onClick（GameObject.SetActive）打开面板，
/// 一旦场景被重复保存、按钮被复制、或预制体改结构，onClick 就会指向失效对象，
/// 表现就是"点了没反应、Console 也没有任何报错"。
/// 这里在每个场景加载后按名字找一次按钮，额外挂一个打开回调（不删原来的），
/// 并打印日志，方便确认点击到底有没有进来。
/// </summary>
public static class PanelLauncher
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Bootstrap()
    {
        SceneManager.sceneLoaded -= OnSceneLoaded;
        SceneManager.sceneLoaded += OnSceneLoaded;
        Bind();
    }

    private static void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        Bind();
    }

    private static void Bind()
    {
        BindButton("jiliBtn", "AdConfirm", AdConfirm.OpenFromButton);
        BindButton("cebianBtn", "cebianPanel", cebian.OpenPanel);
    }

    private static void BindButton(string buttonName, string panelName, UnityEngine.Events.UnityAction open)
    {
        GameObject go = GameObject.Find(buttonName);
        if (go == null)
            return;

        Button button = go.GetComponent<Button>();
        if (button == null)
        {
            Debug.LogWarning("[UI] " + buttonName + " 上没有 Button 组件，无法打开 " + panelName);
            return;
        }

        button.onClick.RemoveListener(open);
        button.onClick.AddListener(open);
    }
}
