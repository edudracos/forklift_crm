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

def add_new_customer_menu():
    st.subheader("Add New Customer")
    name = st.text_input("Name")
    contact_details = st.text_area("Contact Details")

    if st.button("Add Customer"):
        # Generate a unique ID for the new customer
        new_customer_id = len(customers_db.fetch().items) + 1

        # Retrieve existing forklifts, service parts, and sales from their respective bases
        forklifts_data = list(forklifts_db.fetch().items)
        service_parts_data = list(service_parts_db.fetch().items)
        sales_data = list(sales_db.fetch().items)

        # Convert forklift data to a list of Forklift objects
        forklifts = [Forklift(**data) for data in forklifts_data]

        # Convert service part data to a list of ServicePart objects
        service_parts = [ServicePart(**data) for data in service_parts_data]

        # Convert sale data to a list of Sale objects
        sales = [Sale(**data) for data in sales_data]

        new_customer = Customer(id=new_customer_id, name=name, contact_details=contact_details, forklifts=forklifts, service_parts=service_parts, sales=sales)
        customers_db.put(new_customer.__dict__)
        st.success(f"Customer '{name}' added successfully!")
        st.info("Please refresh the page to see the updated customer list.")

def main():
    st.title("Forklift Company CRM")

    # Retrieve existing customer data from the Deta.sh Base
    customers_data = list(customers_db.fetch().items)

    # Check if there are any customers in the database
    if not customers_data:
        st.error("No customers found. Please add a customer first.")
        add_new_customer_menu()
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
        forklift_name = st.text_input("Forklift Name")
        forklift_price = st.number_input("Forklift Price", step=0.01)

        if st.button("Add Forklift"):
            # Generate a unique ID for the new forklift
            new_forklift_id = len(forklifts_db.fetch().items) + 1
            new_forklift = Forklift(id=new_forklift_id, name=forklift_name, price=forklift_price)
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
    def add_item():
        st.subheader("Add an Item")
        sale_id = st.number_input("Sale ID", step=1)
        product_name = st.text_input("Product Name")
        product_price = st.number_input("Product Price", step=0.01)
        item_quantity = st.number_input("Quantity", step=1)

        if st.button("Add Item"):
            sales_data = sales_db.fetch()
            selected_sale_data = [sale for sale in sales_data.items if sale["id"] == sale_id]
            if selected_sale_data:
                selected_sale = Sale(**selected_sale_data[0])
                if product_name in [forklift.name for forklift in selected_sale.items]:
                    product = Forklift(id=0, name=product_name, price=product_price)
                else:
                    product = ServicePart(id=0, name=product_name, price=product_price)

                new_item = Item(product=product, quantity=item_quantity)
                selected_sale.items.append(new_item)
                sales_db.put(selected_sale.__dict__)
                st.success("Item added to sale successfully!")
            else:
                st.error("Sale not found. Please enter a valid Sale ID.")

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


    def associate_item():
        st.subheader("Associate Item with Customer")
        customer_names = [customer.name for customer in customers]
        selected_customer_name = st.selectbox("Select a customer", customer_names)
        selected_customer = [customer for customer in customers if customer.name == selected_customer_name][0]

        item_type = st.radio("Select the item type:", ("Service", "Forklift", "Item"))
        if item_type == "Service":
            existing_items_data = list(service_parts_db.fetch().items)
            existing_items = [ServicePart(**data) for data in existing_items_data]
        elif item_type == "Forklift":
            existing_items_data = list(forklifts_db.fetch().items)
            existing_items = [Forklift(**data) for data in existing_items_data]
        elif item_type == "Item":
            existing_forklifts_data = list(forklifts_db.fetch().items)
            existing_forklifts = [Forklift(**data) for data in existing_forklifts_data]
            existing_service_parts_data = list(service_parts_db.fetch().items)
            existing_service_parts = [ServicePart(**data) for data in existing_service_parts_data]
            existing_items = existing_forklifts + existing_service_parts

        if existing_items:
            existing_item_names = [item.name for item in existing_items]
            selected_item_name = st.selectbox(f"Select a {item_type}", existing_item_names)
            selected_item = [item for item in existing_items if item.name == selected_item_name][0]

            if st.button("Associate Item"):
                if not selected_customer.sales:
                    new_sale_id = len(sales_db.fetch().items) + 1
                    selected_customer.add_sale(Sale(id=new_sale_id, date=datetime.datetime.now(), items=[], total_cost=0.0))


                if item_type == "Service":
                    selected_customer.add_service_part(selected_item.to_dict())
                elif item_type == "Forklift":
                    selected_customer.add_forklift(selected_item)
                elif item_type == "Item":
                    selected_item_price = selected_item.price
                    is_paid = st.checkbox("Is Paid", value=False)
                    item_product = Forklift(id=0, name=selected_item_name, price=selected_item_price) if isinstance(selected_item, Forklift) else ServicePart(id=0, name=selected_item_name, price=selected_item_price)
                    item = Item(product=item_product, quantity=1, is_paid=is_paid)
                    selected_customer.sales[0].items.append(item)

                # Convert the selected_customer object to JSON using the custom encoder
                selected_customer_json = json.dumps(selected_customer.__dict__, cls=CustomJSONEncoder)

                # Update the data in the Deta database
                customers_db.put(json.loads(selected_customer_json))  # Convert back from JSON to dictionary

                st.success(f"{item_type} '{selected_item_name}' associated with customer '{selected_customer_name}' successfully!")
        else:
            st.warning(f"No {item_type}s found. Please add {item_type.lower()}s first.")


    def mark_item_as_paid_or_unpaid():
        st.title("Mark Item as Paid or Unpaid")
        selected_customer = get_selected_customer()
        if selected_customer is None:
            st.warning("Please select a customer first.")
            return

        associated_items = []
        for sale in selected_customer.sales:
            for item in sale.items:
                if isinstance(item.product, Forklift):
                    associated_items.append(item.product)
                elif isinstance(item.product, ServicePart):
                    associated_items.append(item.product)
                else:
                    associated_items.append(item.product.product)
    
    # Display associated items
        if associated_items:
            st.write("Items associated with the customer:")
            for item in associated_items:
                st.write(f"- {item.name} ({item.item_type})")

            item_type = st.radio("Select item type to mark as Paid/Unpaid:", ["Item", "Service", "Forklift"])
        
            associated_item_names = []
            for sale in selected_customer.sales:
                for item in sale.items:
                    if isinstance(item.product, Forklift):
                        associated_item_names.append(item.product.name)
                    elif isinstance(item.product, ServicePart):
                        associated_item_names.append(item.product.name)
                    else:
                        associated_item_names.append(item.product.product.name)

            selected_item = st.selectbox("Select item:", associated_item_names)
        
            status = st.radio("Mark as:", ["Paid", "Unpaid"])
        
            if st.button("Mark"):
                if item_type == "Item":
                # Update the status of the selected item
                    for sale in selected_customer.sales:
                        for item in sale.items:
                            if isinstance(item.product, Forklift) and item.product.name == selected_item:
                                item.product.paid = status == "Paid"
                            elif isinstance(item.product, ServicePart) and item.product.name == selected_item:
                                item.product.paid = status == "Paid"
                            elif isinstance(item.product, Item) and item.product.product.name == selected_item:
                                item.product.paid = status == "Paid"
                
                # Update the Deta database with the modified customer data
                    selected_customer_json = json.dumps(selected_customer.__dict__, cls=CustomJSONEncoder)
                    customers_db.put(selected_customer_json, encoder=CustomJSONEncoder)
                
                    st.success(f"{selected_item} marked as {status}.")
                else:
                    st.error("Marking as Paid/Unpaid is only available for Items.")
        else:
            st.write("No items associated with the customer.")

    menu_options = [
        "Add New Customer",
        "View Customer Details",
        "Add a Forklift",
        "Add a Service Part",
        "Add an Item",
        "Associate Item with Customer",
        "Mark Item as Paid or Unpaid",
    ]

    choice = st.sidebar.selectbox("Select an option", menu_options)

    if choice == "Add New Customer":
        add_new_customer_menu()
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
    elif choice == "Associate Item with Customer":
        associate_item()
    elif choice == "Mark Item as Paid or Unpaid":
        mark_item_as_paid_or_unpaid()

if __name__ == "__main__":
    main()

