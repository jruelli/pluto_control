# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from . import proginit as pi


class PlutoApp:
    def __init__(self, firebase_key_path, log_callback):
        self.log_callback = log_callback
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(firebase_key_path)  # Update with the path to your service account key JSON file
        firebase_admin.initialize_app(cred)
        # Get a Firestore client
        self.db = firestore.client()
        # Subscribe to the "orders" collection
        self.subscribe_to_orders()

    # Function to add data to Firestore with a specific document ID
    def add_data_to_firestore(self, collection_name, document_id, data):
        try:
            # Add a new document with a specific ID
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.set(data)

            # Retrieve the document to get the address
            doc = doc_ref.get()
            if doc.exists:
                self.log_callback(f"Added to {collection_name} with ID {document_id}", "firebase-send: ")
                pi.logger.debug(f"Data added successfully to {collection_name} with ID {document_id}!")
        except Exception as e:
            pi.logger.error("Error adding data to Firestore:", e)

    # Function to update the status of a delivery option
    def update_delivery_status(self, document_id, new_status):
        try:
            doc_ref = self.db.collection('plutito').document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
                if doc_data.get("ordering_state") != new_status:
                    doc_ref.update({
                        "ordering_state": new_status,
                        "last_updated": datetime.now()
                    })
                    self.log_callback(f"Status updated to '{new_status}' for document ID: {document_id}", "firebase-send")
                else:
                    print(f"Document ID {document_id} already has status '{new_status}'")
            else:
                print(f"Document ID {document_id} does not exist in plutito collection.")
        except Exception as e:
            print("Error updating status:", e)

    # Function to subscribe to the "orders" collection
    def subscribe_to_orders(self):
        try:
            orders_ref = self.db.collection('orders')
            orders_ref.on_snapshot(self.on_orders_snapshot)
            print("Subscribed to orders collection successfully!")
        except Exception as e:
            print("Error subscribing to orders collection:", e)

    # Callback function for orders collection snapshot
    def on_orders_snapshot(self, col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                new_order = change.document.to_dict()
                order_id = change.document.id
                print(f"New order added: {order_id} - {new_order}")

                # Extract the address field from the new order
                address = new_order.get('address', 'Address not provided')
                self.log_callback(f"Address: {address}", "firebase-receive: ")

                # Process the address as needed
                # Example: You can add additional processing logic here

                # Create a new document in the "plutito" collection with "processing" status
                plutito_data = {
                    "ordering_state": "processing",
                    "last_updated": datetime.now()
                }
                self.add_data_to_firestore('plutito', order_id, plutito_data)
            elif change.type.name == 'REMOVED':
                order_id = change.document.id
                print(f"Order deleted: {order_id}")
                # Optionally, handle the removal from the 'plutito' collection if needed
                self.remove_data_from_firestore('plutito', order_id)
            elif change.type.name == 'MODIFIED':
                modified_order = change.document.to_dict()
                order_id = change.document.id
                print(f"Order modified: {order_id} - {modified_order}")
                # Handle modifications as needed
                # For example, update the corresponding document in the 'plutito' collection
                self.update_data_in_firestore('plutito', order_id, modified_order)

    # Function to remove data from Firestore
    def remove_data_from_firestore(self, collection_name, document_id):
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
            self.log_callback(f"Removed from {collection_name} with ID {document_id}", "firebase-send: ")
            pi.logger.debug(f"Data removed successfully from {collection_name} with ID {document_id}!")
        except Exception as e:
            pi.logger.error("Error removing data from Firestore:", e)

    # Function to update data in Firestore
    def update_data_in_firestore(self, collection_name, document_id, data):
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.update(data)
            self.log_callback(f"Updated {collection_name} with ID {document_id}", "firebase-send")
            pi.logger.debug(f"Data updated successfully in {collection_name} with ID {document_id}!")
        except Exception as e:
            pi.logger.error("Error updating data in Firestore:", e)
