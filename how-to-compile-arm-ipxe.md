On an arm alma-linux:

dnf install git gcc binutils make perl mtools xz-devel.aarch64
git clone https://github.com/ipxe/ipxe.git
cd ipxe/src
make bin-arm64-efi/ipxe.efi

copy resulting bin-arm64-efi/ipxe.efi as files/ipxe_arm64.efi
