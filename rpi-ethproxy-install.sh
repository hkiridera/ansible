---
- hosts: rpi-ethproxy
  become: no
  roles:
   - rpi-ethproxy
