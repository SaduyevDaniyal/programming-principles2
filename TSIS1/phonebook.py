import csv
import json
from connect import get_connection


def execute_sql_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def get_or_create_group(cur, group_name):
    if not group_name:
        group_name = "Other"

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE LOWER(name) = LOWER(%s)", (group_name,))
    return cur.fetchone()[0]


def add_contact(name, email=None, birthday=None, group_name="Other", phones=None, overwrite=False):
    phones = phones or []

    with get_connection() as conn:
        with conn.cursor() as cur:
            group_id = get_or_create_group(cur, group_name)

            cur.execute("SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s)", (name,))
            existing = cur.fetchone()

            if existing and not overwrite:
                print(f"Skipped duplicate contact: {name}")
                return

            if existing and overwrite:
                contact_id = existing[0]
                cur.execute(
                    """
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s
                    """,
                    (email, birthday or None, group_id, contact_id)
                )
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            else:
                cur.execute(
                    """
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (name, email, birthday or None, group_id)
                )
                contact_id = cur.fetchone()[0]

            for phone_item in phones:
                phone = phone_item.get("phone")
                phone_type = phone_item.get("type", "mobile")

                if phone and phone_type in ("home", "work", "mobile"):
                    cur.execute(
                        "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, phone, phone_type)
                    )

        conn.commit()


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    print("\n" + "-" * 100)
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Email: {row[2] or '-'}")
        print(f"Birthday: {row[3] or '-'}")
        print(f"Group: {row[4] or '-'}")
        print(f"Phones: {row[5] or '-'}")
        print("-" * 100)


def list_contacts(group=None, email=None, sort_by="name", limit=10, offset=0):
    allowed_sort = {
        "name": "c.name",
        "birthday": "c.birthday",
        "date": "c.created_at"
    }

    order_column = allowed_sort.get(sort_by, "c.name")

    query = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS group_name,
            COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE (%s IS NULL OR LOWER(g.name) = LOWER(%s))
          AND (%s IS NULL OR c.email ILIKE %s)
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order_column}
        LIMIT %s OFFSET %s
    """

    email_pattern = f"%{email}%" if email else None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (group, group, email, email_pattern, limit, offset)
            )
            rows = cur.fetchall()

    print_contacts(rows)


def search_all_fields():
    pattern = input("Search name / email / phone: ")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            rows = cur.fetchall()

    print_contacts(rows)


def filter_sort_menu():
    group = input("Group filter, press Enter to skip: ").strip() or None
    email = input("Email search, press Enter to skip: ").strip() or None
    sort_by = input("Sort by name / birthday / date: ").strip().lower() or "name"

    if sort_by not in ("name", "birthday", "date"):
        sort_by = "name"

    list_contacts(group=group, email=email, sort_by=sort_by)


def pagination_loop():
    limit = input("Page size: ").strip()
    limit = int(limit) if limit.isdigit() else 5
    offset = 0

    while True:
        list_contacts(limit=limit, offset=offset)

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Unknown command.")


def export_to_json(filename="contacts.json"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name AS group_name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.name
                """
            )
            contacts = cur.fetchall()

            result = []
            for contact in contacts:
                contact_id, name, email, birthday, group_name = contact

                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s",
                    (contact_id,)
                )
                phones = [
                    {"phone": phone, "type": phone_type}
                    for phone, phone_type in cur.fetchall()
                ]

                result.append({
                    "name": name,
                    "email": email,
                    "birthday": birthday.isoformat() if birthday else None,
                    "group": group_name,
                    "phones": phones
                })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

    print(f"Exported to {filename}")


def import_from_json(filename="contacts.json"):
    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    for item in contacts:
        name = item["name"]

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s)", (name,))
                duplicate = cur.fetchone()

        overwrite = False
        if duplicate:
            choice = input(f"Contact '{name}' already exists. skip / overwrite? ").strip().lower()
            if choice == "skip":
                print(f"Skipped {name}")
                continue
            elif choice == "overwrite":
                overwrite = True
            else:
                print("Unknown choice. Skipped.")
                continue

        add_contact(
            name=name,
            email=item.get("email"),
            birthday=item.get("birthday"),
            group_name=item.get("group", "Other"),
            phones=item.get("phones", []),
            overwrite=overwrite
        )


def import_from_csv(filename="contacts.csv"):
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            add_contact(
                name=row["name"],
                email=row.get("email"),
                birthday=row.get("birthday"),
                group_name=row.get("group", "Other"),
                phones=[{
                    "phone": row.get("phone"),
                    "type": row.get("type", "mobile")
                }],
                overwrite=False
            )

    print("CSV import completed.")


def add_phone_console():
    name = input("Contact name: ")
    phone = input("Phone: ")
    phone_type = input("Type home / work / mobile: ").strip().lower()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()

    print("Phone added.")


def move_group_console():
    name = input("Contact name: ")
    group_name = input("New group: ")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()

    print("Contact moved.")


def add_contact_console():
    name = input("Name: ")
    email = input("Email: ") or None
    birthday = input("Birthday YYYY-MM-DD, press Enter to skip: ") or None
    group = input("Group Family / Work / Friend / Other: ") or "Other"

    phones = []
    while True:
        phone = input("Phone, press Enter to stop: ")
        if not phone:
            break

        phone_type = input("Type home / work / mobile: ").strip().lower()
        if phone_type not in ("home", "work", "mobile"):
            phone_type = "mobile"

        phones.append({"phone": phone, "type": phone_type})

    add_contact(name, email, birthday, group, phones)
    print("Contact added.")


def main():
    while True:
        print("""
PHONEBOOK EXTENDED

1. Create schema
2. Create procedures and functions
3. Add contact
4. Add phone to existing contact
5. Move contact to group
6. Search all fields
7. Filter / email search / sort
8. Paginated navigation
9. Import CSV
10. Export JSON
11. Import JSON
0. Exit
""")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                execute_sql_file("schema.sql")
                print("Schema created.")
            elif choice == "2":
                execute_sql_file("procedures.sql")
                print("Procedures created.")
            elif choice == "3":
                add_contact_console()
            elif choice == "4":
                add_phone_console()
            elif choice == "5":
                move_group_console()
            elif choice == "6":
                search_all_fields()
            elif choice == "7":
                filter_sort_menu()
            elif choice == "8":
                pagination_loop()
            elif choice == "9":
                filename = input("CSV filename, Enter for contacts.csv: ") or "contacts.csv"
                import_from_csv(filename)
            elif choice == "10":
                filename = input("JSON filename, Enter for contacts.json: ") or "contacts.json"
                export_to_json(filename)
            elif choice == "11":
                filename = input("JSON filename, Enter for contacts.json: ") or "contacts.json"
                import_from_json(filename)
            elif choice == "0":
                break
            else:
                print("Unknown option.")
        except Exception as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
