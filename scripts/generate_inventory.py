#!/usr/bin/env python3
"""
Скрипт для генерации actual_servers.yml на основе пинга доменов
"""

import argparse
import socket
import sys
from typing import Dict, List, Optional

import yaml


def ping_domain(domain: str, timeout: int = 3) -> Optional[str]:
    """
    Пингует домен и возвращает IP-адрес, если домен доступен
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None


def generate_inventory(
    start_num: int,
    end_num: int,
    domain_template: str = "vpn-{}.tgvpnbot.com",
    output_file: str = "actual_servers.yml",
    ansible_user: str = "vpnuser",
    ansible_port: int = 11041,
) -> None:
    """
    Генерирует inventory файл на основе пинга доменов
    """

    print(f"🔍 Пингуем домены от {start_num} до {end_num}...")

    inventory = {
        "all": {
            "children": {"servers": {"hosts": {}}},
            "hosts": {"localhost": {"ansible_connection": "local"}},
        }
    }

    successful_pings = 0
    failed_pings = 0

    for num in range(start_num, end_num + 1):
        domain = domain_template.format(num)
        print(f"  Пингуем {domain}...", end=" ")

        ip = ping_domain(domain)

        if ip:
            print(f"✅ {ip}")
            successful_pings += 1

            # Определяем имя сервера
            if num == 8:
                server_name = "router-1"
            elif num == 61:
                server_name = "router-2"
            else:
                server_name = f"server-{num}"

            # Добавляем сервер в inventory
            inventory["all"]["children"]["servers"]["hosts"][f"server-{num}"] = {
                "ansible_host": ip,
                "ansible_user": ansible_user,
                "ansible_port": ansible_port,
                "server_domain": domain,
                "server_name": server_name,
            }
        else:
            print("❌ недоступен")
            failed_pings += 1

    # Сохраняем inventory в файл
    print(f"\n💾 Сохраняем inventory в {output_file}...")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("all:\n")
            f.write("    children:\n")
            f.write("        servers:\n")
            f.write("            hosts:\n")

            # Записываем каждый сервер с пустой строкой между ними
            server_hosts = inventory["all"]["children"]["servers"]["hosts"]
            for i, (server_name, server_data) in enumerate(server_hosts.items()):
                f.write(f"                {server_name}:\n")
                f.write(
                    f"                    ansible_host: {server_data['ansible_host']}\n"
                )
                f.write(
                    f"                    ansible_user: {server_data['ansible_user']}\n"
                )
                f.write(
                    f"                    ansible_port: {server_data['ansible_port']}\n"
                )
                f.write(
                    f'                    server_domain: "{server_data["server_domain"]}"\n'
                )
                f.write(
                    f'                    server_name: "{server_data["server_name"]}"\n'
                )
                #                f.write(f"                    ansible_ssh_private_key_file: /etc/ansible/migration/ssh_keys/id_ed25519\n")
                #                f.write(f"                    ansible_backup_files:\n")
                #                f.write(f"                        - /etc/x-ui/x-ui.db\n")

                # Добавляем пустую строку между серверами (кроме последнего)
                if i < len(server_hosts) - 1:
                    f.write("\n")

            f.write("\n")
            f.write("    hosts:\n")
            f.write("        localhost:\n")
            f.write("            ansible_connection: local\n")

        print(f"✅ Inventory успешно сохранен!")
        print(f"📊 Статистика:")
        print(f"   - Успешных пингов: {successful_pings}")
        print(f"   - Неудачных пингов: {failed_pings}")
        print(f"   - Всего проверено: {successful_pings + failed_pings}")

        if successful_pings > 0:
            print(f"\n🎯 Найдено {successful_pings} активных серверов:")
            for server_name, server_data in inventory["all"]["children"]["servers"][
                "hosts"
            ].items():
                print(
                    f"   - {server_name}: {server_data['ansible_host']} ({server_data['server_domain']})"
                )

    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Генерация actual_servers.yml на основе пинга доменов vpn-*.tgvpnbot.com"
    )

    parser.add_argument("start", type=int, help="Начальный номер сервера (например, 2)")

    parser.add_argument("end", type=int, help="Конечный номер сервера (например, 5)")

    parser.add_argument(
        "--domain-template",
        default="vpn-{}.tgvpnbot.com",
        help="Шаблон домена (по умолчанию: vpn-{}.tgvpnbot.com)",
    )

    parser.add_argument(
        "--output",
        default="actual_servers.yml",
        help="Имя выходного файла (по умолчанию: actual_servers.yml)",
    )

    parser.add_argument(
        "--ansible-user",
        default="vpnuser",
        help="Пользователь Ansible (по умолчанию: vpnuser)",
    )

    parser.add_argument(
        "--ansible-port", type=int, default=11041, help="Порт SSH (по умолчанию: 11041)"
    )

    args = parser.parse_args()

    if args.start > args.end:
        print("❌ Ошибка: начальный номер не может быть больше конечного")
        sys.exit(1)

    print(f"🚀 Генерация inventory для серверов {args.start}-{args.end}")
    print(f"📁 Выходной файл: {args.output}")
    print(f"👤 Пользователь: {args.ansible_user}")
    print(f"🔌 Порт: {args.ansible_port}")
    print()

    generate_inventory(
        start_num=args.start,
        end_num=args.end,
        domain_template=args.domain_template,
        output_file=args.output,
        ansible_user=args.ansible_user,
        ansible_port=args.ansible_port,
    )


if __name__ == "__main__":
    main()
