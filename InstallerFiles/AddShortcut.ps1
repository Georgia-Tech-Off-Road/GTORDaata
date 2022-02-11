$batchName = 'Run DAATA'
$batchPath="C:\Program Files (x86)\GTOR DAATA\InstallerFiles\RunDAATA.bat"
$objShell = New-Object -ComObject WScript.Shell
$objShortCut = $objShell.CreateShortcut("C:\Program Files (x86)\GTOR DAATA\GTOR DAATA.lnk")
$objShortCut.TargetPath = $batchPath
$objShortCut.IconLocation = "C:\Program Files\GTOR DAATA\InstallerFiles\icon_GTORLogo.ico"
$objShortCut.Save()

$batchName = 'Run DAATA'
$batchPath="C:\Program Files (x86)\GTOR DAATA\InstallerFiles\RunDAATA.bat"
$objShell = New-Object -ComObject WScript.Shell
$objShortCut = $objShell.CreateShortcut("$Home\Desktop\GTOR DAATA.lnk")
$objShortCut.TargetPath = $batchPath
$objShortCut.IconLocation = "C:\Program Files\GTOR DAATA\InstallerFiles\icon_GTORLogo.ico"
$objShortCut.Save()