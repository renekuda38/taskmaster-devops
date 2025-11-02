import json

# = = = = = =   =    NACITANIE A PARSOVANIE JSON SUBORU (.json -> .py dictionary)    =   = = = = = =

all_data = []  # list na všetky JSON objekty 

with open("health_check.json", "r") as file:
    json_object = "" # string, do kt. budeme ukladat riadky pre jeden JSON objekt
    
    # pocitadlo pre kontrolu otvorenych/zatvorenych zatvoriek
    # aby sme vedeli, kedy sme nacitali kompletny cely jeden objekt
    counter = 0 

    # prejdeme uplne vsetky riadky v subore .json -> postupne prejdeme vsetky objekty, kt. sa tam nachadzaju
    for line in file:
        # ak je riadok prazdny (obsahuje iba medzery alebo \n), tak ho preskocime
        # line.strip() vracia text/string - odstrani medzery a \n
        # line.strip() = TRUE ak sa tam nachadza text
        # line.strip() = FALSE ak sa tam nenanachadza text
        # ked nie je pravda, ze obsahuje text -> pokracuj
        if not line.strip():  
            continue

        counter += line.count('{') # narazime na otvaraciu zatvorku -> zvysime pocitadlo

        json_object += line # pridame aktualny riadok k rozpracovanemu JSON objektu

        counter -= line.count('}') # narazime na uzatvaraciu zatvorku -> zmensime pocitadlo

        # ak je pocitadlo na 0, znamena, ze sa prave jeden JSON objekt uzavrel - zaznam jedneho objektu je kompletny
        if counter == 0: # and json_object.strip(): # DOISTOTY: counter je 0 a riadok obsahuje text ( "}" ) -> spusti riadky

            # json.loads() prevedie string, kt. je v JSON formate na python dictionary
            data = json.loads(json_object) 

            # ziskany dictionary pridame do listu, kde budu casom ulozene vsetky JSON objekty v dictionary formate
            all_data.append(data) 

            # vyprazdnime premennu, aby sme do nej mohli ukladat nasledujuci JSON objekt
            json_object = ""


# = = = = = =   =    VYTVARANIE MARKDOWN REPORTU & AGREGACIA DAT    =   = = = = = =


with open("health_report.md", "w") as report:

    report.write("# Health Check Report\n\n")

    # # # --- CPU agregacia ---

    cpu_values = [] # list na vsetky cpu hodnoty

    # obj je prave jeden JSON objekt - t.j. zaznam ohraniceny { }
    # all_data - vsetky objekty, list jednotlivych zaznamov
    for obj in all_data:
        
        # kazdy objekt obsahuje cpu_usage hodnotu
        cpu_usage=(obj["cpu_usage"])

        # cpu_usage hodnotu z jednotlivych objektov pridame do listu cpu_values
        cpu_values.append(cpu_usage)

    # urobime priemer hodnot z listu, kde su ulozene hodnoty cpu_usage zo vsetkych objektov
    average_cpu = sum(cpu_values) / len(cpu_values)

    # # # # MIGHT DELETE LATER
    print(f"Average CPU usage: {average_cpu:.2f}")

    
    # CPU average usage info vypis
    report.write(f"## CPU Usage\n")
    report.write(f"Average: {average_cpu:.2f}%\n\n")


    # # # --- disk agregacia ---

    # disk_values = dictionary, kde:
        # kluc = nazov disku ("/")
        # hodnota = list hodnot pre tento disk
        # priklad: print(disk_values) ->  {'/boot': [31, 26, 40], '/': [15, 10, 17], '/boot/efi': [2, 2, 5]}
    disk_values = {}

    # average_disk = {}

    # prejdeme vsetky nacitane objekty v all_data
    for obj in all_data:

        # z objektu vyberieme dictionary s disk usage
        # napriklad: {"/boot": 31, "/": 15, "/boot/efi": 2}
        disks = obj["disk_usage"]

        # prejdeme vsetky disky v tomto dictionary
        for disk_name in disks:

            # ziskame hodnotu usage pre konkretny jeden disk
            disk_usage = disks[disk_name]

            # ak sa disk este nenachadza v dictionary disk_values, vytvorime prazny list
            if disk_name not in disk_values:
                disk_values[disk_name] = []

            # ziskanu hodnotu zapise do listu pre konkretny disk
            # disk_values je dictionary
            # disk_values[disk_name] je konkretny list v dictionary -> eg. '/boot': [31, 26, 40]
            disk_values[disk_name].append(disk_usage)

        # average_disk[disk_name] = sum(disk_values[disk_name]) / len(disk_values[disk_name])

    # Disk usage info vypis
    report.write(f"## Disk Usage\n\n")

    for disk in disk_values:
        average_usage = sum(disk_values[disk]) / len(disk_values[disk])
        min_usage = min(disk_values[disk])
        max_usage = max(disk_values[disk])
        print(f"Average disk usage of {disk}: {average_usage:.2f}")
        report.write(f"**{disk}**\n")
        report.write(f"- Average: {average_usage:.2f}%\n")
        report.write(f"- Min: {min_usage}%\n")
        report.write(f"- Max: {max_usage}%\n\n")

