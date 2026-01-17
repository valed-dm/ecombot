# EcomBot User Checkout Workflow & Manual Testing Guide

This document outlines the user flows for the checkout process, including Delivery and Pickup scenarios. Use this as a checklist for manual testing.

## Prerequisites
- **Admin Panel**: Use `/admin` to configure settings.
- **Delivery Mode**: Toggle "Global Delivery" in Admin -> Delivery Settings.
- **Pickup Points**: Create/Active pickup points in Admin -> Delivery Settings -> Manage Pickup Points.
- **Delivery Types**: Activate courier options (e.g., Local Same Day) in Admin -> Delivery Settings -> Manage Delivery Types.

---

## 1. Fast Path (Returning User)
*User has a saved Phone Number (and Address if delivery is active).*

### Scenario A: Delivery Enabled (Courier Available)
**Setup**: `DELIVERY=True`, at least one non-pickup Delivery Option active. User has saved Address & Phone.
1.  **Action**: User clicks "Checkout" in Cart.
2.  **Expected**:
    - Bot shows "Fast Checkout" confirmation.
    - Displays saved **Delivery Address**.
    - Shows Total Price (including delivery fee if applicable).
    - Buttons: [Confirm Order], [Edit Details], [Cancel].
3.  **Action**: Click [Confirm Order].
4.  **Expected**: Success message with Order #. Admin notified.

### Scenario B: Pickup Only (Multiple Points)
**Setup**: `DELIVERY=False` OR no courier options active. Multiple active Pickup Points. User has saved Phone.
1.  **Action**: User clicks "Checkout".
2.  **Expected**: Bot asks "📍 Please select a pickup point" with buttons for each point.
3.  **Action**: Select a Pickup Point.
4.  **Expected**:
    - Bot shows "Fast Checkout" confirmation.
    - Displays **Selected Pickup Point**.
    - Buttons: [Confirm Order], [Edit Details], [Cancel].
5.  **Action**: Click [Confirm Order].
6.  **Expected**: Success message.

### Scenario C: Pickup Only (Single Point)
**Setup**: `DELIVERY=False`. Only 1 active Pickup Point. User has saved Phone.
1.  **Action**: User clicks "Checkout".
2.  **Expected**:
    - Bot automatically selects the single pickup point.
    - Shows confirmation immediately.
3.  **Action**: Click [Confirm Order].
4.  **Expected**: Success message.

---

## 2. Slow Path (First-Time User / Missing Info)
*User profile is incomplete.*

### Scenario D: Delivery Enabled
**Setup**: `DELIVERY=True`. User has NO saved info.
1.  **Action**: User clicks "Checkout".
2.  **Expected**: Bot says info is missing. Asks for **Name**.
3.  **Action**: Enter Name.
4.  **Expected**: Bot asks for **Phone Number** (Request Contact button).
5.  **Action**: Share Contact or type number.
6.  **Expected**: Bot asks for **Delivery Address**.
7.  **Action**: Enter Address.
8.  **Expected**:
    - Bot shows Confirmation summary (Name, Phone, Address).
    - Buttons: [Confirm Order], [Cancel].
9.  **Action**: Click [Confirm Order].
10. **Expected**: Success message. User profile updated with Phone/Address.

### Scenario E: Pickup Only
**Setup**: `DELIVERY=False`. User has NO saved info. Multiple Pickup Points.
1.  **Action**: User clicks "Checkout".
2.  **Expected**: Bot asks for **Name**.
3.  **Action**: Enter Name.
4.  **Expected**: Bot asks for **Phone**.
5.  **Action**: Share Contact.
6.  **Expected**:
    - Bot skips address step.
    - Bot asks to **Select a Pickup Point**.
7.  **Action**: Select Point.
8.  **Expected**:
    - Bot shows Confirmation summary (Name, Phone, Pickup Point).
    - Buttons: [Confirm Order], [Cancel].
9.  **Action**: Click [Confirm Order].
10. **Expected**: Success message.

---

## 3. Edge Cases & Validation

- **Empty Cart**: Click Checkout with 0 items -> Error message.
- **No Pickup Points**: `DELIVERY=False` and 0 active pickup points -> Error message "No pickup points available".
- **Stock Check**: Try to order more items than available in stock -> Error message during confirmation.
- **Cancel**: Click [Cancel] during confirmation -> Checkout cancelled, cart remains.