https://<wazuh-dashboard-ip>:443
PaPli4VxuX5vHarhf7?FYFqLArDrhf+?
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.5-1.msi -OutFile $env:tmp\wazuh-agent; msiexec.exe /i $env:tmp\wazuh-agent /q WAZUH_MANAGER='10.0.2.15' WAZUH_AGENT_NAME='WIndows-agent' 
