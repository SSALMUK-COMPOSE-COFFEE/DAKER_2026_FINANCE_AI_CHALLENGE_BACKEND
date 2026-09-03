#!/usr/bin/env bash
set -euo pipefail

USERNAME=pullim
GROUPNAME=pullim
OWNER=hajinkwonsee
PROJECT=/home/hajinkwonsee/developments/hackathon/DAKER_2026_FINANCE_AI_CHALLENGE

# 누나들 public key
PUBKEYS=(
  'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHyajUCv9Rjl9ns+1XB2qgoFd8gIOwuRlnYiHZ3cDyWU pullim 김주현'
  'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGcS/BvPOoYcx1FXtTikizf/XkvrnOoOeHQzeu81HvkU pullim 채수지'
)

[ "$(id -u)" -eq 0 ] || { echo "root로 실행하세요: sudo bash $0"; exit 1; }
[ -d "$PROJECT" ] || { echo "프로젝트 폴더가 없습니다: $PROJECT"; exit 1; }

getent group "$GROUPNAME" >/dev/null || groupadd "$GROUPNAME"
if id -u "$USERNAME" >/dev/null 2>&1; then
  usermod -s /bin/bash "$USERNAME"
else
  useradd -m -d "/home/$USERNAME" -s /bin/bash -g "$GROUPNAME" "$USERNAME"
fi
usermod -aG "$GROUPNAME" "$OWNER"

install -d -m 700 -o "$USERNAME" -g "$GROUPNAME" "/home/$USERNAME/.ssh"
printf '%s\n' "${PUBKEYS[@]}" > "/home/$USERNAME/.ssh/authorized_keys"
chown "$USERNAME:$GROUPNAME" "/home/$USERNAME/.ssh/authorized_keys"
chmod 600 "/home/$USERNAME/.ssh/authorized_keys"


chmod o+x /home/hajinkwonsee /home/hajinkwonsee/developments /home/hajinkwonsee/developments/hackathon
chgrp -R "$GROUPNAME" "$PROJECT"
chmod -R g+rwX "$PROJECT"
find "$PROJECT" -type d -exec chmod g+s {} +

ln -sfn "$PROJECT" "/home/$USERNAME/project"
chown -h "$USERNAME:$GROUPNAME" "/home/$USERNAME/project"

cat > /etc/ssh/sshd_config.d/99-zz-pullim.conf <<CONF
Match User $USERNAME
    AllowTcpForwarding no
    AllowAgentForwarding no
    X11Forwarding no
    PermitTunnel no
CONF

sshd -t
systemctl reload ssh
echo "완료. 현재 세션은 그대로 두고 새 터미널에서 접속을 확인하세요."
echo "접속: ssh -i ~/.ssh/pullim_chaesuji pullim@hajin.xyz"
