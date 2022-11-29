from zion.database import Database, Setting


class settings(Database):
    def __init__(self, database):
        self.session = database.session
        self.engine = database.engine

    # Get setting from database
    def get_setting(self, setting_name: str) -> Setting | bool:
        return self._get_from_db(Setting.setting_name, setting_name)

    # Change setting in database
    def change_setting(self, setting_name: str, setting_value: str) -> bool:
        setting = self.get_setting(setting_name)
        # Check if setting exits in db
        if not setting:
            return False

        return self._alt_in_db(Setting, {"setting_value":
                               setting_value}, setting.id)

    # Add setting to database
    def add_setting(self, setting_name: str, setting_value: str,
                    setting_desc: str, setting_type: str) -> bool:
        if (self._exists_in_table(Setting.setting_name, setting_name)):
            return False

        return self._add_to_db(Setting(setting_name=setting_name,
                                       setting_value=setting_value,
                                       setting_desc=setting_desc,
                                       setting_type=setting_type))

    def get_settings(self) -> dict:
        settings_ = dict()
        settings = self._get_all_from_db(Setting)
        if len(settings) < 1:
            return False

        for setting in settings:
            settings_[setting.setting_name] = [setting.setting_value,
                                               setting.setting_desc,
                                               setting.setting_type]

        return settings_
