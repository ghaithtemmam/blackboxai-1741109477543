import csv
import io
from typing import List, Dict, Tuple
import pandas as pd
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileParser:
    REQUIRED_COLUMNS = ['username', 'name']
    
    @staticmethod
    async def parse_csv(file: UploadFile) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Parse CSV file and validate required columns.
        Returns tuple of (parsed_data, errors).
        """
        errors = []
        try:
            # Read file content
            content = await file.read()
            df = pd.read_csv(io.BytesIO(content))
            
            # Convert column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Validate required columns
            missing_columns = [col for col in FileParser.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return [], errors
            
            # Remove duplicate usernames
            df = df.drop_duplicates(subset=['username'])
            
            # Remove rows with empty usernames
            df = df.dropna(subset=['username'])
            
            # Convert DataFrame to list of dictionaries
            parsed_data = df.to_dict('records')
            
            # Validate data
            for idx, row in enumerate(parsed_data):
                # Ensure username is string
                row['username'] = str(row['username']).strip()
                if not row['username']:
                    errors.append(f"Empty username found at row {idx + 2}")
                    continue
                
                # Ensure name is string
                row['name'] = str(row.get('name', '')).strip()
            
            # Remove rows with errors
            parsed_data = [row for row in parsed_data if row['username']]
            
            logger.info(f"Successfully parsed CSV with {len(parsed_data)} valid entries")
            return parsed_data, errors

        except pd.errors.EmptyDataError:
            errors.append("The CSV file is empty")
            return [], errors
        except Exception as e:
            errors.append(f"Error parsing CSV file: {str(e)}")
            return [], errors

    @staticmethod
    async def parse_instagram_accounts_csv(file: UploadFile) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Parse CSV file containing Instagram account credentials.
        Returns tuple of (parsed_accounts, errors).
        """
        errors = []
        try:
            content = await file.read()
            df = pd.read_csv(io.BytesIO(content))
            
            # Convert column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Check required columns
            required_columns = ['username', 'password']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return [], errors
            
            # Remove duplicates and empty values
            df = df.drop_duplicates(subset=['username'])
            df = df.dropna(subset=['username', 'password'])
            
            # Convert to list of dictionaries
            accounts = df.to_dict('records')
            
            # Validate each account
            valid_accounts = []
            for idx, account in enumerate(accounts):
                # Validate username
                username = str(account['username']).strip()
                if not username:
                    errors.append(f"Empty username found at row {idx + 2}")
                    continue
                
                # Validate password
                password = str(account['password']).strip()
                if not password:
                    errors.append(f"Empty password found for username {username}")
                    continue
                
                valid_accounts.append({
                    'username': username,
                    'password': password
                })
            
            logger.info(f"Successfully parsed {len(valid_accounts)} Instagram accounts from CSV")
            return valid_accounts, errors

        except pd.errors.EmptyDataError:
            errors.append("The CSV file is empty")
            return [], errors
        except Exception as e:
            errors.append(f"Error parsing Instagram accounts CSV: {str(e)}")
            return [], errors

    @staticmethod
    def process_template_variables(template: str, user_data: Dict[str, str]) -> str:
        """
        Replace template variables with user data.
        Example: "Hi {name}!" -> "Hi John!"
        """
        try:
            # Create a copy of user_data with lowercase keys
            data = {k.lower(): v for k, v in user_data.items()}
            
            # Replace all variables in template
            processed = template
            for key, value in data.items():
                placeholder = "{" + key + "}"
                processed = processed.replace(placeholder, str(value))
            
            return processed
        except Exception as e:
            logger.error(f"Error processing template variables: {str(e)}")
            return template

# Initialize file parser
file_parser = FileParser()
