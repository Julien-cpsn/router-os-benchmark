qemu-system-x86_64 \
  -m 8G \
  mininet-vm-x86_64.vmdk \
  -net nic,model=virtio \
  -net user,net=192.168.101.0/24,hostfwd=tcp::8022-:22 \
  -virtfs local,path="$(pwd)/shared",mount_tag=shared,security_model=mapped-xattr \
  -nographic \
  -machine accel=kvm \
  -enable-kvm