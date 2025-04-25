virt-builder debian-12 \
  --output debian-bookworm.qcow2 \
  --format qcow2 \
  --size 6G \
  --root-password password:debian \
  --upload /etc/apt/sources.list:/etc/apt/sources.list \
  --install "netperf,iperf3,fping,irtt,htop,net-tools,flent"