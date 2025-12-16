#!/bin/bash
cd /etc/ansible/iperf
ansible-playbook -i inventory.yml iperf_playbook.yml
