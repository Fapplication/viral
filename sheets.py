import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import SHEET_CREDENTIALS, SPREADSHEET_ID, POINTS_PER_REFERRAL

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class Sheets:
    def __init__(self):
        creds = Credentials.from_service_account_file(SHEET_CREDENTIALS, scopes=SCOPES)
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key(SPREADSHEET_ID)
        self._init_sheets()

    def _init_sheets(self):
        """Create sheets with headers if they don't exist."""
        existing = [s.title for s in self.sheet.worksheets()]

        if "Users" not in existing:
            ws = self.sheet.add_worksheet("Users", 1000, 10)
            ws.append_row(["UserID","Username","FullName","ReferrerID",
                           "Referrals","Points","JoinedAt","Claimed"])

        if "Referrals" not in existing:
            ws = self.sheet.add_worksheet("Referrals", 5000, 5)
            ws.append_row(["ReferrerID","ReferredID","ReferredName","Timestamp"])

    def _users(self):
        return self.sheet.worksheet("Users")

    def _referrals(self):
        return self.sheet.worksheet("Referrals")

    def _find_user_row(self, user_id):
        """Returns (row_index, row_data) or (None, None)."""
        ws = self._users()
        try:
            cell = ws.find(str(user_id), in_column=1)
            if cell:
                return cell.row, ws.row_values(cell.row)
        except:
            pass
        return None, None

    def register_user(self, user_id, username, full_name, referrer_id=None):
        """Register user. Returns True if new, False if existing."""
        row, _ = self._find_user_row(user_id)
        if row:
            return False  # Already exists

        ws = self._users()
        ws.append_row([
            str(user_id),
            username,
            full_name,
            str(referrer_id) if referrer_id else "",
            0,   # Referrals
            0,   # Points
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            ""   # Claimed
        ])
        return True

    def get_user(self, user_id):
        """Returns user dict or None."""
        ws = self._users()
        records = ws.get_all_records()
        for r in records:
            if str(r.get("UserID")) == str(user_id):
                return r
        return None

    def add_referral(self, referrer_id, referred_id, referred_name):
        """Credit referrer with points and increment count."""
        # Log referral
        self._referrals().append_row([
            str(referrer_id),
            str(referred_id),
            referred_name,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ])

        # Update referrer stats
        ws = self._users()
        row, data = self._find_user_row(referrer_id)
        if row:
            headers = ws.row_values(1)
            refs_col = headers.index("Referrals") + 1
            pts_col  = headers.index("Points") + 1
            current_refs = int(ws.cell(row, refs_col).value or 0)
            current_pts  = int(ws.cell(row, pts_col).value or 0)
            ws.update_cell(row, refs_col, current_refs + 1)
            ws.update_cell(row, pts_col,  current_pts  + POINTS_PER_REFERRAL)
            return current_pts + POINTS_PER_REFERRAL
        return 0

    def get_leaderboard(self, limit=10):
        """Returns top users sorted by referrals."""
        ws = self._users()
        records = ws.get_all_records()
        sorted_users = sorted(records, key=lambda r: int(r.get("Referrals", 0)), reverse=True)
        return sorted_users[:limit]

    def get_rank(self, user_id):
        """Returns rank of user by referrals."""
        ws = self._users()
        records = ws.get_all_records()
        sorted_users = sorted(records, key=lambda r: int(r.get("Referrals", 0)), reverse=True)
        for i, r in enumerate(sorted_users):
            if str(r.get("UserID")) == str(user_id):
                return i + 1
        return "—"

    def get_all_users(self):
        return self._users().get_all_records()

    def mark_claimed(self, user_id, reward_refs):
        """Add reward level to claimed list."""
        ws = self._users()
        row, data = self._find_user_row(user_id)
        if row:
            headers = ws.row_values(1)
            claimed_col = headers.index("Claimed") + 1
            current = ws.cell(row, claimed_col).value or ""
            existing = current.split(",") if current else []
            if str(reward_refs) not in existing:
                existing.append(str(reward_refs))
            ws.update_cell(row, claimed_col, ",".join(existing))
