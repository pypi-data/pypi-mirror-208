# Standard library imports
from collections import namedtuple


class gsheetPlayer:
    """
    A class that represents a player in a sheet row

    ...

    Attributes
    ----------
    person : array
        an array with each sheet column value.  Contains date, name, email, etc
    row : int
        the sheet row number where player was read from
    gsheet : dict
        information about the gsheet including:
            - spreadsheetId
            - sheetId
            - sheetName

    Methods
    -------
    cid_upgrade()
        returns Stripe Upgrade Charge ID from player membership purchase
    cid_upgrade(value)
        sets Stripe Upgrade Charge ID for player to val
    free()
        returns if player gets free membership
    get_values()
        returns if player gets free membership
    gsheet()
        returns gsheet information dictionary
    league_count()
        returns number of leagues a player is registered for on USTA
    league_count(value)
        sets number of leagues a player is registered for on USTA
    league_list()
        returns list of leagues a player is registered for on USTA
    league_list(value)
        sets list of leagues a player is registered for on USTA
    name_first()
        returns player first name as entered
    name_last()
        returns player last name as entered
    name_process()
        Removes duplicate last name for player from faulty form input
    name_proper()
        returns player name properly capitalized
    paid()
        returns about paid by player
    paid(value)
        sets amount paid by player
    spreadsheet_id()
        returns spreadsheet_id from gsheet dictionary
    sheet_id()
        returns sheet_id from gsheet dictionary
    sheet_name()
        returns sheet_name from gsheet dictionary

    """

    def __init__(
        self,
        person_list,
        row,
        gsheet={},
    ):
        self.field_names = "date name email phone ntrp usta gender age paid vol cid uid league_count league_list notes"
        Person = namedtuple(
            "Person",
            self.field_names,
            defaults=[
                None,
                None,
                None,
                None,
                0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                0,
                [],
                None,
            ],
        )
        p = Person(*person_list)

        self.original_line = person_list
        self.date = p.date
        self.name = p.name
        self.email = p.email
        self.phone = p.phone
        self.ntrp = p.ntrp
        self.usta = p.usta
        self.gender = p.gender
        self.age = p.age
        self.__paid = p.paid
        self.vol = p.vol
        self.__cid = p.cid
        self.__uid = p.uid
        if not p.league_count:
            self.league_count = 0
        else:
            self.league_count = int(p.league_count)
        # self.league_count = int(p.league_count)
        if p.league_list:
            self.league_list = p.league_list.split(",")
        else:
            self.league_list = []
        self.row = row
        self.__gsheet = gsheet
        self.__email_clubrep_date = None

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other):
        return self.name == other.name

    @property
    def cid(self):
        if self.__cid:
            return self.__cid.rstrip()
        else:
            return self.__cid

    @property
    def cid_upgrade(self):
        return self.__cid_upgrade

    @cid_upgrade.setter
    def cid_upgrade(self, value):
        self.__cid_upgrade = value

    @property
    def dump(self):
        data = {}
        data["field_names"] = self.field_names
        data["original"] = self.original_line
        data["row"] = self.row
        data["email_clubrep_date"] = self.email_clubrep_date
        data["league_list"] = []
        if self.league_list:
            for team in self.league_list:
                data["league_list"].append(team)
        data["gsheet"] = {}
        data["gsheet"]["spreadsheetId"] = self.spreadsheet_id
        data["gsheet"]["sheetId"] = self.sheet_id
        data["gsheet"]["sheetName"] = self.sheet_name
        return data

    @property
    def email_clubrep_date(self):
        if self.__email_clubrep_date:
            return self.__email_clubrep_date
        else:
            return None

    @email_clubrep_date.setter
    def email_clubrep_date(self, value):
        self.__email_clubrep_date = value

    @property
    def free(self):
        if "FREE" in self.cid:
            return True
        else:
            return False

    @property
    def get_values(self):
        values = [
            [
                self.date,
                self.name,
                self.email,
                self.phone,
                self.ntrp,
                self.usta,
                self.gender,
                self.age,
                self.__paid,
                self.vol,
                self.cid,
                self.uid,
            ],
        ]
        return values

    @property
    def gsheet(self):
        return self.__gsheet

    @property
    def league_count(self):
        if self.__league_count:
            return self.__league_count

    @league_count.setter
    def league_count(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("positive integer expected")
        self.__league_count = value

    @property
    def league_list(self):
        if self.__league_list:
            return self.__league_list

    @league_list.setter
    def league_list(self, value):
        if not isinstance(value, list):
            raise ValueError("expected array")
        self.__league_list = value

    @property
    def name_first(self):
        try:
            return self.name.split()[0]
        except IndexError:
            return None

    @property
    def name_last(self):
        try:
            return self.name.split()[-1]
        except IndexError:
            return None

    @property
    def name_lower(self):
        try:
            return self.name.lower()
        except IndexError:
            return None

    @property
    def name_first_lower(self):
        try:
            return self.name.split()[0].lower()
        except IndexError:
            return None

    @property
    def name_last_lower(self):
        try:
            return self.name.split()[-1].lower()
        except IndexError:
            return None

    @property
    def name_process(self):
        """
        Eliminate duplicate lastname due to form input mistakes
        Capitalize properly
        """
        seen = set()
        result = []
        for item in self.name.split():
            if item not in seen:
                if item.islower() or (item.isupper() and len(item) > 2):
                    item = item.title()
                seen.add(item)
                result.append(item)
        newName = " ".join(result)
        if self.name != newName:
            print(f"Name changed from {self.__name} to {newName}")
            self.__name = " ".join(result)

    @property
    def name_proper(self):
        firstname = self.name_first
        lastname = self.name_last
        if lastname and firstname and lastname in firstname:
            firstname = firstname.replace(lastname, "").strip()
        if firstname and (firstname.islower() or firstname.isupper()):
            firstname = firstname.title()
        if lastname and (lastname.islower() or lastname.isupper()):
            lastname = lastname.title()
        return f"{firstname} {lastname}"

    @property
    def paid(self):
        return int(self.__paid)

    @paid.setter
    def paid(self, value):
        if isinstance(value, str) and "$" in value:
            self.__paid = int(value.strip("$"))
        elif not value:
            self.__paid = 0
        else:
            self.__paid = value

    @property
    def spreadsheet_id(self):
        return self.__gsheet["spreadsheetId"]

    @property
    def sheet_id(self):
        return self.__gsheet["sheetId"]

    @property
    def sheet_name(self):
        return self.__gsheet["sheetName"]

    @property
    def uid(self):
        if self.__uid:
            return self.__uid.rstrip()
        else:
            return self.__uid
