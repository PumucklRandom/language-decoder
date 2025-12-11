Set WshShell = CreateObject("WScript.Shell")

' set environment variables (comment out with a leading apostrophe if not needed)
' WshShell.Environment("Process")("http_proxy") = "http://localhost:3128"
' WshShell.Environment("Process")("https_proxy") = "http://localhost:3128"

' change working directory to script folder
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' run pythonw.exe with your script
WshShell.Run ".\python\pythonw.exe .\__main__.py", 0, False