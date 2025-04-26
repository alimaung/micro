Disable-PnpDevice -InstanceId $deviceId -Confirm:$false
Start-Sleep -Seconds 2
Enable-PnpDevice -InstanceId $deviceId -Confirm:$false