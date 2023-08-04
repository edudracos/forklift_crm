import streamlit as st
import secrets
from deta import Deta
from customer import Customer
from forklift import Forklift
from service_part import ServicePart
from sale import Sale
from item import Item
import json
import datetime


# Initialize Deta with your Deta.sh API key
deta = Deta(st.secrets["DETA_KEY"])  
customers_db = deta.Base("customers") 
forklifts_db = deta.Base("forklifts")  
service_parts_db = deta.Base("service_parts")  
sales_db = deta.Base("sales")  

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, Forklift):
            return obj.__dict__
        if isinstance(obj, ServicePart):
            return obj.__dict__
        if isinstance(obj, Sale):
            return obj.__dict__
        if isinstance(obj, Item):
            return obj.__dict__
        return super().default(obj)
    
def get_selected_customer(selected_customer_name):
    customer_data = customers_db.fetch().items.get(selected_customer_name)
    if customer_data:
        customer_data.pop('key', None)
        return Customer(**customer_data)
    return None
def add_new_customer_to_db(new_customer):
    customers_db.put(new_customer.__dict__)

def add_new_customer():
    st.subheader("Add New Customer")
    name = st.text_input("Name")
    phone_number = st.text_input("Phone Number")
    address = st.text_input("Address")
    email = st.text_input("Email")
    contact_details = st.text_area("Contact Details")
    notes = st.text_area("Notes")

    if st.button("Add Customer", key="check_1"):
        # Generate a unique ID for the new customer
        new_customer_id = len(customers_db.fetch().items) + 1

        new_customer = Customer(
            id=new_customer_id,
            name=name,
            phone_number=phone_number,
            address=address,
            email=email,
            contact_details=contact_details,
            notes=notes
        )
        add_new_customer_to_db(new_customer)
        st.success(f"Customer '{name}' added successfully!")
        st.info("Please refresh the page to see the updated customer list.")

def main():
    st.title("Forklift Company CRM")

    # Retrieve existing customer data from the Deta.sh Base
    customers_data = list(customers_db.fetch().items)

    # Check if there are any customers in the database
    if not customers_data:
        st.error("No customers found. Please add a customer first.")
        add_new_customer()
        return

    # Convert customer data to a list of Customer objects
    customers = []
    for data in customers_data:
        # Remove the 'key' attribute from the data dictionary
        data.pop('key', None)

        # Remove the 'total_owed' attribute from the data dictionary if present
        data.pop('total_owed', None)

        customer = Customer(**data)
        customers.append(customer)

    # Helper function to add a new forklift
    def add_forklift():
        st.subheader("Add a Forklift")
        forklift_year = st.text_input("Forklift Year")
        forklift_model= st.text_input("Forklift Model")
        forklift_brand= st.text_input("Forklift Brand")
        forklift_vin= st.text_input("Forklift Vin")
        forklift_price = st.number_input("Forklift Price", step=0.01)

        if st.button("Add Forklift"):
            # Generate a unique ID for the new forklift
            new_forklift_id = len(forklifts_db.fetch().items) + 1
            new_forklift = Forklift(id=new_forklift_id, year=forklift_year, model=forklift_model, brand=forklift_brand, vin=forklift_vin, price=forklift_price)
            forklifts_db.put(new_forklift.__dict__)

            st.success(f"Forklift '{forklift_name}' added successfully!")

    # Helper function to add a new service part
    def add_service_part():
        st.subheader("Add a Service Part")
        part_name = st.text_input("Service Part Name")
        part_price = st.number_input("Service Part Price", step=0.01)

        if st.button("Add Service Part"):
            # Generate a unique ID for the new service part
            new_part_id = len(service_parts_db.fetch().items) + 1
            new_part = ServicePart(id=new_part_id, name=part_name, price=part_price)
            service_parts_db.put(new_part.__dict__)

            st.success(f"Service Part '{part_name}' added successfully!")

    # Helper function to add a new item to a sale
    
    def add_item(selected_customer, selected_sale, item):
        selected_sale.items.append(item)
        customers_db.put(selected_customer.__dict__)

    def add_sale(selected_customer, sale):
        selected_customer.sales.append(sale)
        customers_db.put(selected_customer.__dict__)

    # Helper function to display customer details
    def display_customer_details(customer):
        st.subheader(f"Customer: {customer.name}")
        st.write(f"ID: {customer.id}")
        st.write(f"Contact Details: {customer.contact_details}")

        # Display forklifts
        if customer.forklifts:
            st.subheader("Forklifts:")
            for forklift in customer.forklifts:
                paid_status = "Paid" if forklift.is_paid else "Unpaid"
                st.write(f"- {forklift.name} (Price: ${forklift.price:.2f}) - {paid_status}")

        # Display service parts
        if customer.service_parts:
            st.subheader("Service Parts:")
            for service in customer.service_parts:
                paid_status = "Paid" if service.is_paid else "Unpaid"
                st.write(f"- {service.name} (Price: ${service.price:.2f}) - {paid_status}")

        # Display sales
        if customer.sales:
            st.subheader("Sales:")
            for sale in customer.sales:
                paid_status = "Paid" if all(item.is_paid for item in sale.items) else "Unpaid"
                st.write(f"Sale ID: {sale.id}, Date: {sale.date}, Total Cost: ${sale.total_cost:.2f} - {paid_status}")
                st.write("Items:")
                for item in sale.items:
                    item_name = item.product.name
                    item_price = item.product.price
                    item_quantity = item.quantity
                    paid_status = "Paid" if item.is_paid else "Unpaid"
                    st.write(f"- {item_name} (Price: ${item_price:.2f}), Quantity: {item_quantity} - {paid_status}")

    def mark_service_payment(customer, service_name, is_paid):
        customer.mark_service_as_paid(service_name) if is_paid else customer.mark_service_as_unpaid(service_name)
        customers_db.put(customer.__dict__)

    def mark_forklift_payment(customer, forklift_name, is_paid):
        customer.mark_forklift_as_paid(forklift_name) if is_paid else customer.mark_forklift_as_unpaid(forklift_name)
        customers_db.put(customer.__dict__)

    def mark_item_payment(customer, item_name, is_paid):
        customer.mark_item_as_paid(item_name) if is_paid else customer.mark_item_as_unpaid(item_name)
        customers_db.put(customer.__dict__)

    def manage_items(selected_customer):
        st.subheader("Manage Items")

        st.write(f"Customer: {selected_customer.name}")
        st.write(f"Total Debt: ${selected_customer.total_owed:.2f}")

        existing_items_data = list(service_parts_db.fetch().items) + list(forklifts_db.fetch().items)
        existing_items = [ServicePart(**data) if "is_paid" in data else Forklift(**data) for data in existing_items_data]
        existing_item_names = [item.name for item in existing_items]

        selected_item_name = st.selectbox("Select an item", existing_item_names)

        item = next((item for item in existing_items if item.name == selected_item_name), None)

        if not item:
            st.error("Selected item not found.")
            return

        associated_items = set()
        for sale in selected_customer.sales:
            for sale_item in sale.items:
                if sale_item.product.name == selected_item_name:
                    associated_items.add(sale.id)

        if associated_items:
            st.write("Items associated with the customer:")
            for sale_id in associated_items:
                st.write(f"- Sale ID: {sale_id}")

        action_type = st.radio("Select action", ["Associate Item", "Mark as Paid", "Mark as Unpaid"])

        if action_type == "Associate Item":
            if selected_item_name in existing_item_names:
                sale_id = st.number_input("Sale ID", min_value=1, step=1)
                is_paid = st.checkbox("Is Paid", value=False)

                new_item = Item(product=item, quantity=1, is_paid=is_paid)
                sale = next((sale for sale in selected_customer.sales if sale.id == sale_id), None)

                if sale:
                    add_item(selected_customer, sale, new_item)
                    st.success(f"Item '{selected_item_name}' associated with customer '{selected_customer.name}' successfully.")
                else:
                    st.error("Sale not found. Please enter a valid Sale ID.")

        elif action_type in ["Mark as Paid", "Mark as Unpaid"]:
            for sale in selected_customer.sales:
                for sale_item in sale.items:
                    if sale_item.product.name == selected_item_name:
                        sale_item.is_paid = action_type == "Mark as Paid"
                        customers_db.put(selected_customer.__dict__)
                        st.success(f"Item '{selected_item_name}' marked as {'Paid' if action_type == 'Mark as Paid' else 'Unpaid'}.")
                        return
        elif action_type == "Associate Item":
            if selected_item_name in existing_item_names:
                sale_id = st.number_input("Sale ID", min_value=1, step=1)
                is_paid = st.checkbox("Is Paid", value=False)

                new_item = Item(product=item, quantity=1, is_paid=is_paid)
                sale = next((sale for sale in selected_customer.sales if sale.id == sale_id), None)

                if sale:
                    add_item(selected_customer, sale, new_item)
                    st.success(f"Item '{selected_item_name}' associated with customer '{selected_customer.name}' successfully.")
                else:
                    st.error("Sale not found. Please enter a valid Sale ID.")

            st.error("Selected item is not associated with the customer.")




    menu_options = [
        "Add New Customer",
        "View Customer Details",
        "Add a Forklift",
        "Add a Service Part",
        "Add an Item",
        "Manage Items",
    ]

    choice = st.sidebar.selectbox("Select an option", menu_options)

    if choice == "Add New Customer":
        add_new_customer()
    elif choice == "View Customer Details":
        if not customers:
            st.warning("No customers found. Please add a customer first.")
        else:
            customer_names = [customer.name for customer in customers]
            selected_customer_name = st.selectbox("Select a customer", customer_names)
            selected_customer = [customer for customer in customers if customer.name == selected_customer_name][0]
            display_customer_details(selected_customer)
    elif choice == "Add a Forklift":
        add_forklift()
    elif choice == "Add a Service Part":
        add_service_part()
    elif choice == "Add an Item":
        add_item()
    elif choice == "Manage Items":
        manage_items()

        selected_customer_name = st.selectbox("Select a customer", customer_names)
        selected_customer = get_selected_customer(selected_customer_name)
        manage_items(selected_customer)

if __name__ == "__main__":
    from customer import Customer
    from forklift import Forklift
    from service_part import ServicePart
    from sale import Sale
    from item import Item
    main()

