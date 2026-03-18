@echo off

::WPS相关的进程会高占用
::taskkill /f /im wps.exe /t
taskkill /f /im wpscloudsvr.exe /t
taskkill /f /im wpscenter.exe /t
taskkill /f /im BackgroundDownload.exe  /t


::任务管理器中会在电脑空闲时, CPU高占用的 Microsoft Compatibility Telemetry
::进程本体：CompatTelRunner.exe，位于 C:\Windows\System32\CompatTelRunner.exe
taskkill /f /im CompatTelRunner.exe
::禁用触发它的计划任务（最关键）
schtasks /Change /TN "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser" /DISABLE
schtasks /Change /TN "\Microsoft\Windows\Application Experience\ProgramDataUpdater" /DISABLE
::关闭配套 DiagTrack 遥测服务（可选）
sc stop DiagTrack
sc config DiagTrack start= disabled
::图形界面对照（方便确认）
::计划任务：`taskschd.msc`
::路径：任务计划程序库 → Microsoft → Windows → **Application Experience**，禁用：
::Microsoft Compatibility Appraiser
::ProgramDataUpdater
::服务：`services.msc`
::找到：**连接的用户体验和遥测（DiagTrack）** → 停止，启动类型改为「禁用」。
