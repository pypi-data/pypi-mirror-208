def save_updates(entity_type, task, old_settings, new_kwargs):
    now = datetime.now()
    for key, value in new_kwargs.items():
        try:
            old_value = old_settings[key].name
        except:
            old_value = old_settings[key]
        self.repo.add(
            Event(entity_type, task, now, key,
                  old_value, value))

