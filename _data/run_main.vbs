' Name: AppName
' Version: 0.0.0.0
' Create windows script shell object
Set WScriptShell = CreateObject("WScript.Shell")

' set environment variables for proxy
' WScriptShell.Environment("Process")("http_proxy") = "http://localhost:3128"
' WScriptShell.Environment("Process")("https_proxy") = "http://localhost:3128"

' change working directory to script folder
WScriptShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' run python main script
' WScriptShell.Run(".\python\python.exe .\__main__.py")
WScriptShell.Run(".\python\pythonw.exe .\__main__.py")
