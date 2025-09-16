# railway.nix
{ pkgs, ... }: {
  # Add system-level packages here.
  # For example, to install libgl1 and libsm6 for OpenCV.
  environment.systemPackages = with pkgs; [
    libgl1
    libsm6
  ];
}