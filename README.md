> [!WARNING]
> This is a PhD project, and it is still very WIP.

# Router OS performance benchmark

This repository aims to benchmark router operating system network performances. It uses [mininet](https://mininet.org/) with [iPerf3](https://github.com/esnet/iperf).

## Before using

> [!INFO]
> This tutorial comes from https://mininet.org/vm-setup-notes/

1. Download the latest mininet vm, e.g. `mininet-2.3.0-210211-ubuntu-20.04.1-legacy-server-amd64-ovf.zip`
2. Unzip it
3. Move `mininet-vm-x86_64.vmdk` to the root of this directory
4. Insure you have [qemu](https://www.qemu.org/download/) installed with `qemu-system-x86_64` available

## How to use

### On your host machine

Launch the mininet vm.

```shell
./launch-mininet.sh
```

> [!INFO]
> On the host machine, quit qemu with `Ctrl-a`, then `x`

Connect to the mininet vm through ssh.

```shell
ssh -Y -p 8022 mininet@localhost
```

> [!INFO]
> Password: mininet

### On the mininet VM

#### Once

```shell
sudo apt install qemu-system
sudo apt install -y bindfs
sudo mkdir -p /mnt/shared

sudo pip install --upgrade pip
sudo python -m pip install matplotlib
```

#### At every startup

```shell
sudo mount -t 9p -o trans=virtio,version=9p2000.L shared /mnt/shared
sudo bindfs --map=501/1000:@dialout/@1000 /mnt/shared /mnt/shared
cd /mnt/shared
````

#### Usage examples

Single test example

```shell
sudo python main.py -vvv --runs 3 single sonic vms/sonic-vs-202411.img unix vms/debian-12-nocloud-amd64.raw
```

Many tests example

```shell
sudo python main.py -vvv --runs 3 many resources/test_list.json vms/debian-12-nocloud-amd64.raw
```

## Others

### Nested KVM support for QEMU

You may want to enable nested KVM support in your host machine if not done yet

```shell
rmmod kvm_intel
modprobe kvm_intel nested=1
```

Verification (`Y` means it's activated)

```shell
cat /sys/module/kvm_intel/parameters/nested
```