import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import threading

class DatabaseManager:
    def __init__(self, db_path: str = 'hotel_system.db'):
        self.db_path = db_path
        self.local = threading.local()
        self.init_database()
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hotels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                location TEXT,
                description TEXT,
                pdf_filename TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Bookings table (hotel-specific)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id INTEGER NOT NULL,
                guest_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                details TEXT,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (hotel_id) REFERENCES hotels (id)
            )
        ''')
        
        # Tasks table (hotel-specific)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id INTEGER NOT NULL,
                task_description TEXT NOT NULL,
                assigned_to TEXT,
                priority TEXT DEFAULT 'medium',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (hotel_id) REFERENCES hotels (id)
            )
        ''')
        
        # Guest sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guest_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                hotel_id INTEGER,
                guest_name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hotel_id) REFERENCES hotels (id)
            )
        ''')
        
        conn.commit()
        
        # Add sample hotels if none exist
        self.add_sample_hotels()
    
    def add_sample_hotels(self):
        """Add sample hotels if database is empty"""
        hotels = self.get_all_hotels()
        if not hotels:
            sample_hotels = [
                {
                    'name': 'Grand Palace Hotel',
                    'location': 'New York City',
                    'description': 'Luxury 5-star hotel in the heart of Manhattan with premium amenities',
                    'pdf_filename': 'grand_palace_policies.pdf'
                },
                {
                    'name': 'Seaside Resort & Spa',
                    'location': 'Miami Beach',
                    'description': 'Beachfront resort with world-class spa facilities and ocean views',
                    'pdf_filename': 'seaside_resort_policies.pdf'
                },
                {
                    'name': 'Mountain View Lodge',
                    'location': 'Aspen, Colorado',
                    'description': 'Cozy mountain retreat with stunning alpine views and ski access',
                    'pdf_filename': 'mountain_view_policies.pdf'
                }
            ]
            
            for hotel in sample_hotels:
                self.add_hotel(hotel)
    
    def add_hotel(self, hotel_data: Dict[str, Any]) -> int:
        """Add new hotel to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO hotels (name, location, description, pdf_filename)
            VALUES (?, ?, ?, ?)
        ''', (
            hotel_data['name'],
            hotel_data.get('location', ''),
            hotel_data.get('description', ''),
            hotel_data.get('pdf_filename', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_all_hotels(self) -> List[Dict[str, Any]]:
        """Get all active hotels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hotels WHERE is_active = 1 ORDER BY name')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_hotel_by_id(self, hotel_id: int) -> Optional[Dict[str, Any]]:
        """Get hotel by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hotels WHERE id = ? AND is_active = 1', (hotel_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_booking(self, hotel_id: int, booking_data: Dict[str, Any]) -> int:
        """Add booking for specific hotel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookings (hotel_id, guest_name, service_type, details)
            VALUES (?, ?, ?, ?)
        ''', (
            hotel_id,
            booking_data.get('guest_name', 'Guest'),
            booking_data.get('service_type', ''),
            booking_data.get('details', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def add_task(self, hotel_id: int, task_data: Dict[str, Any]) -> int:
        """Add task for specific hotel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (hotel_id, task_description, assigned_to, priority)
            VALUES (?, ?, ?, ?)
        ''', (
            hotel_id,
            task_data.get('description', ''),
            task_data.get('assigned_to', 'Front Desk'),
            task_data.get('priority', 'medium')
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_hotel_bookings(self, hotel_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get bookings for specific hotel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE hotel_id = ? 
            ORDER BY booking_date DESC 
            LIMIT ?
        ''', (hotel_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_hotel_tasks(self, hotel_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tasks for specific hotel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE hotel_id = ? 
            ORDER BY created_date DESC 
            LIMIT ?
        ''', (hotel_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]