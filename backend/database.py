import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from models import InstagramAccount, Template, DMCampaignStatus
from config import settings

class Database:
    def __init__(self):
        self.accounts_file = settings.ACCOUNTS_DB_PATH
        self.templates_file = settings.TEMPLATES_DB_PATH
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        """Ensure the data directory exists and create initial JSON files if needed."""
        os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
        
        if not os.path.exists(self.accounts_file):
            self._write_json(self.accounts_file, {"accounts": []})
        if not os.path.exists(self.templates_file):
            self._write_json(self.templates_file, {"templates": []})

    def _read_json(self, file_path: str) -> Dict:
        """Read JSON file with error handling."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _write_json(self, file_path: str, data: Dict):
        """Write to JSON file with error handling."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            raise Exception(f"Failed to write to {file_path}: {str(e)}")

    # Instagram Account Methods
    def add_account(self, account: InstagramAccount) -> bool:
        """Add a new Instagram account."""
        data = self._read_json(self.accounts_file)
        accounts = data.get("accounts", [])
        
        # Check if account already exists
        if any(acc["username"] == account.username for acc in accounts):
            return False
        
        accounts.append(account.dict())
        self._write_json(self.accounts_file, {"accounts": accounts})
        return True

    def get_account(self, username: str) -> Optional[InstagramAccount]:
        """Get an Instagram account by username."""
        data = self._read_json(self.accounts_file)
        accounts = data.get("accounts", [])
        
        for account in accounts:
            if account["username"] == username:
                return InstagramAccount(**account)
        return None

    def update_account(self, username: str, updates: Dict) -> bool:
        """Update an Instagram account's details."""
        data = self._read_json(self.accounts_file)
        accounts = data.get("accounts", [])
        
        for i, account in enumerate(accounts):
            if account["username"] == username:
                accounts[i].update(updates)
                self._write_json(self.accounts_file, {"accounts": accounts})
                return True
        return False

    def list_accounts(self) -> List[InstagramAccount]:
        """List all Instagram accounts."""
        data = self._read_json(self.accounts_file)
        return [InstagramAccount(**account) for account in data.get("accounts", [])]

    def delete_account(self, username: str) -> bool:
        """Delete an Instagram account."""
        data = self._read_json(self.accounts_file)
        accounts = data.get("accounts", [])
        
        filtered_accounts = [acc for acc in accounts if acc["username"] != username]
        if len(filtered_accounts) != len(accounts):
            self._write_json(self.accounts_file, {"accounts": filtered_accounts})
            return True
        return False

    # Template Methods
    def add_template(self, template: Template) -> str:
        """Add a new message template."""
        data = self._read_json(self.templates_file)
        templates = data.get("templates", [])
        
        # Generate simple ID if not provided
        if not template.id:
            template.id = f"template_{len(templates) + 1}"
        
        templates.append(template.dict())
        self._write_json(self.templates_file, {"templates": templates})
        return template.id

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        data = self._read_json(self.templates_file)
        templates = data.get("templates", [])
        
        for template in templates:
            if template["id"] == template_id:
                return Template(**template)
        return None

    def update_template(self, template_id: str, updates: Dict) -> bool:
        """Update a template's details."""
        data = self._read_json(self.templates_file)
        templates = data.get("templates", [])
        
        for i, template in enumerate(templates):
            if template["id"] == template_id:
                templates[i].update(updates)
                templates[i]["updated_at"] = datetime.now().isoformat()
                self._write_json(self.templates_file, {"templates": templates})
                return True
        return False

    def list_templates(self) -> List[Template]:
        """List all templates."""
        data = self._read_json(self.templates_file)
        return [Template(**template) for template in data.get("templates", [])]

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        data = self._read_json(self.templates_file)
        templates = data.get("templates", [])
        
        filtered_templates = [t for t in templates if t["id"] != template_id]
        if len(filtered_templates) != len(templates):
            self._write_json(self.templates_file, {"templates": filtered_templates})
            return True
        return False

# Initialize database instance
db = Database()
