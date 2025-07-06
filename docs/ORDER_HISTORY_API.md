# Order History & Payment Tracking API Documentation

## Overview
The Order History API provides comprehensive payment tracking, subscription management, and receipt generation for the Garaad platform. This system tracks all payment transactions, including Waafi payments, subscription purchases, and provides detailed order history with downloadable receipts.

## Features
- ✅ Complete order history tracking
- ✅ Waafi payment integration with webhooks
- ✅ Subscription order management
- ✅ Receipt generation and download
- ✅ Payment statistics and analytics
- ✅ Multi-currency support (USD, EUR, SOS)
- ✅ Full Somali language support
- ✅ Automatic premium status updates

## Base URL
```
https://api.garaad.org/api/payment/
```

## Authentication
All endpoints require JWT authentication:
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### 1. Order Management

#### List Order History
```http
GET /api/payment/orders/
```

**Query Parameters:**
- `status` - Filter by order status (pending, completed, failed, etc.)
- `payment_method` - Filter by payment method (waafi, zaad, etc.)
- `start_date` - Filter orders from this date (YYYY-MM-DD)
- `end_date` - Filter orders until this date (YYYY-MM-DD)
- `search` - Search by order number or description
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": "uuid-here",
        "order_number": "GRD-20241201123456-ABCD1234",
        "total_amount": "9.99",
        "currency": "USD",
        "currency_display": "US Dollar",
        "payment_method": "waafi",
        "payment_method_display": "Waafi",
        "payment_method_somali": "Waafi",
        "status": "completed",
        "status_display": "Completed",
        "status_somali": "Dhammaystiran",
        "created_at": "2024-12-01T12:34:56Z",
        "paid_at": "2024-12-01T12:35:30Z",
        "description": "Garaad Monthly Subscription",
        "items_count": 1,
        "subscription_info": {
          "type": "monthly",
          "start_date": "2024-12-01",
          "end_date": "2024-12-31",
          "name": "Ishtiraak Bishii"
        }
      }
    ],
    "pagination": {
      "total_count": 15,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

#### Get Order Details
```http
GET /api/payment/orders/{order_id}/
```

**Response:**
```json
{
  "id": "uuid-here",
  "order_number": "GRD-20241201123456-ABCD1234",
  "total_amount": "9.99",
  "currency": "USD",
  "payment_method": "waafi",
  "status": "completed",
  "created_at": "2024-12-01T12:34:56Z",
  "paid_at": "2024-12-01T12:35:30Z",
  "waafi_transaction_id": "1268666",
  "waafi_reference_id": "REF123456",
  "customer_name": "Ahmed Hassan",
  "customer_email": "ahmed@example.com",
  "description": "Garaad Monthly Subscription",
  "items": [
    {
      "id": 1,
      "item_type": "subscription",
      "name": "Ishtiraak Bishii",
      "description": "Ishtiraak Garaad monthly",
      "unit_price": "9.99",
      "quantity": 1,
      "total_price": "9.99",
      "subscription_type": "monthly",
      "subscription_start_date": "2024-12-01T00:00:00Z",
      "subscription_end_date": "2024-12-31T23:59:59Z"
    }
  ]
}
```

#### Create Subscription Order
```http
POST /api/payment/subscription/create/
```

**Request Body:**
```json
{
  "subscription_type": "monthly",  // monthly, yearly, lifetime
  "payment_method": "waafi",       // waafi, zaad, evcplus, sahal
  "currency": "USD"                // USD, EUR, SOS
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dalbashada waa la sameeyay si guul leh",
  "data": {
    "id": "uuid-here",
    "order_number": "GRD-20241201123456-ABCD1234",
    "total_amount": "9.99",
    "currency": "USD",
    "status": "pending",
    "items": [...]
  }
}
```

### 2. Receipt Management

#### Get Receipt Data
```http
GET /api/payment/orders/{order_id}/receipt/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order_number": "GRD-20241201123456-ABCD1234",
    "customer_name": "Ahmed Hassan",
    "customer_email": "ahmed@example.com",
    "total_amount": "9.99",
    "currency": "USD",
    "payment_method": "Waafi",
    "paid_at": "2024-12-01 12:35:30",
    "description": "Garaad Monthly Subscription",
    "items": [...],
    "company_name": "Garaad",
    "company_address": "Hargeisa, Somaliland",
    "company_email": "info@garaad.org",
    "receipt_date": "2024-12-01 12:40:00",
    "receipt_title": "Rasiidka Bixinta",
    "order_label": "Lambarka Dalbashada",
    "customer_label": "Macaamiilka",
    "amount_label": "Qiimaha",
    "method_label": "Habka Bixinta",
    "date_label": "Taariikh",
    "thank_you_message": "Waad ku mahadsantahay inaad Garaad isticmaasho!"
  }
}
```

#### Download Receipt
```http
GET /api/payment/orders/{order_id}/download_receipt/
```

Returns HTML receipt (can be extended to PDF in production).

### 3. Order Statistics

#### Get User Order Statistics
```http
GET /api/payment/orders/stats/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_orders": 5,
    "total_amount": "149.95",
    "completed_orders": 4,
    "pending_orders": 1,
    "failed_orders": 0,
    "monthly_stats": [
      {
        "month": "2024-12",
        "orders": 2,
        "amount": 19.98
      },
      {
        "month": "2024-11",
        "orders": 1,
        "amount": 99.99
      }
    ],
    "payment_method_stats": {
      "waafi": 3,
      "zaad": 1,
      "admin": 1
    },
    "currency_stats": {
      "USD": {
        "count": 4,
        "total": 139.96
      },
      "SOS": {
        "count": 1,
        "total": 500.0
      }
    },
    "recent_orders": [...]
  }
}
```

### 4. Waafi Payment Integration

#### Waafi Webhook Endpoint
```http
POST /api/payment/webhook/waafi/
```

This endpoint is called by Waafi when payment status changes. It automatically:
- Updates order status
- Activates premium subscriptions
- Creates notifications
- Logs webhook data

**Webhook Payload Example:**
```json
{
  "customerNumber": "252613282000",
  "customerName": "Ahmed Hassan",
  "partnerUID": "MERCHANT_UID",
  "transferInfo": {
    "amount": "10",
    "charges": "0",
    "transferId": "176329573",
    "transferCode": "1017635883",
    "transactionDate": "08/02/23 19:15:38",
    "transferStatus": "3",  // 3 = completed, 4/5 = failed
    "currencySymbol": "$",
    "referenceId": "REF123456",
    "currencyCode": "840",
    "description": "Garaad Monthly Subscription"
  }
}
```

### 5. Premium Status Update (Enhanced)

#### Update Premium Status with Order Tracking
```http
POST /api/auth/update-premium/
```

**Request Body:**
```json
{
  "is_premium": true,
  "subscription_type": "monthly",
  "payment_method": "waafi",
  "amount": 9.99,
  "currency": "USD",
  "waafi_transaction_id": "1268666",
  "waafi_reference_id": "REF123456"
}
```

**Response:**
```json
{
  "message": "Premium status updated successfully",
  "is_premium": true,
  "subscription_type": "monthly",
  "subscription_start_date": "2024-12-01T00:00:00Z",
  "subscription_end_date": "2024-12-31T23:59:59Z",
  "order": {
    "id": "uuid-here",
    "order_number": "GRD-20241201123456-ABCD1234",
    "total_amount": "9.99",
    "currency": "USD",
    "payment_method": "waafi",
    "status": "completed"
  }
}
```

---

## Database Models

### Order Model
```python
class Order(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    order_number = CharField(unique=True)
    total_amount = DecimalField(max_digits=10, decimal_places=2)
    currency = CharField(choices=['USD', 'EUR', 'SOS'])
    payment_method = CharField(choices=['waafi', 'zaad', 'evcplus', ...])
    status = CharField(choices=['pending', 'completed', 'failed', ...])
    created_at = DateTimeField(auto_now_add=True)
    paid_at = DateTimeField(null=True)
    waafi_transaction_id = CharField(null=True)
    waafi_reference_id = CharField(null=True)
    customer_name = CharField(null=True)
    customer_email = EmailField(null=True)
    description = TextField()
    metadata = JSONField()
```

### OrderItem Model
```python
class OrderItem(models.Model):
    order = ForeignKey(Order)
    item_type = CharField(choices=['subscription', 'feature', 'course'])
    name = CharField()
    unit_price = DecimalField(max_digits=10, decimal_places=2)
    quantity = PositiveIntegerField()
    total_price = DecimalField(max_digits=10, decimal_places=2)
    subscription_type = CharField(null=True)
    subscription_start_date = DateTimeField(null=True)
    subscription_end_date = DateTimeField(null=True)
```

---

## Frontend Integration

### 1. Order History Page
```javascript
// Fetch user's order history
const fetchOrderHistory = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/payment/orders/?${params}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example usage
const orders = await fetchOrderHistory({
  status: 'completed',
  page: 1,
  page_size: 10
});
```

### 2. Receipt Download
```javascript
// Download receipt
const downloadReceipt = async (orderId) => {
  const response = await fetch(`/api/payment/orders/${orderId}/download_receipt/`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `receipt-${orderId}.html`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  }
};
```

### 3. Subscription Purchase Flow
```javascript
// Create subscription order
const createSubscription = async (subscriptionData) => {
  const response = await fetch('/api/payment/subscription/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify(subscriptionData)
  });
  return await response.json();
};

// Example usage
const order = await createSubscription({
  subscription_type: 'monthly',
  payment_method: 'waafi',
  currency: 'USD'
});
```

### 4. Order Statistics Dashboard
```javascript
// Fetch order statistics
const fetchOrderStats = async () => {
  const response = await fetch('/api/payment/orders/stats/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example usage
const stats = await fetchOrderStats();
console.log(`Total spent: ${stats.data.total_amount}`);
```

---

## Waafi Payment Integration

### 1. Frontend Widget Integration
```javascript
// Initialize Waafi payment
const initiateWaafiPayment = async (orderData) => {
  // First create the order
  const order = await createSubscription(orderData);
  
  // Initialize Waafi widget with order reference
  const waafiConfig = {
    merchantUid: 'YOUR_MERCHANT_UID',
    amount: order.data.total_amount,
    currency: order.data.currency,
    referenceId: order.data.order_number,
    description: order.data.description,
    successCallback: (result) => {
      // Payment successful - webhook will handle the rest
      window.location.href = '/subscription/success';
    },
    errorCallback: (error) => {
      console.error('Payment failed:', error);
      window.location.href = '/subscription/error';
    }
  };
  
  // Initialize Waafi widget (pseudo-code)
  WaafiPay.initialize(waafiConfig);
};
```

### 2. Webhook Handling
The webhook endpoint (`/api/payment/webhook/waafi/`) automatically:
1. Validates webhook data
2. Updates order status
3. Activates premium subscription
4. Creates user notifications
5. Logs all webhook activity

### 3. Payment Status Checking
```javascript
// Check payment status
const checkPaymentStatus = async (orderId) => {
  const response = await fetch(`/api/payment/orders/${orderId}/`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const order = await response.json();
  return order.status;
};
```

---

## Error Handling

### Common Error Responses
```json
{
  "success": false,
  "error": "Rasiidka kaliya waa la heli karaa dalbashada dhammaystiran"
}
```

### Error Codes
- `400` - Bad Request (missing required fields)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (order not found)
- `500` - Internal Server Error

---

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **User Isolation**: Users can only access their own orders
3. **Webhook Validation**: Waafi webhooks are validated and logged
4. **Data Encryption**: Sensitive payment data is encrypted
5. **Audit Trail**: All payment activities are logged

---

## Testing

### Test Order Creation
```bash
curl -X POST "https://api.garaad.org/api/payment/subscription/create/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_type": "monthly",
    "payment_method": "waafi",
    "currency": "USD"
  }'
```

### Test Order History
```bash
curl -X GET "https://api.garaad.org/api/payment/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Receipt Download
```bash
curl -X GET "https://api.garaad.org/api/payment/orders/ORDER_ID/download_receipt/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o receipt.html
```

---

## Deployment Notes

1. **Environment Variables**: Set Waafi API credentials
2. **Database Migration**: Run payment app migrations
3. **Webhook URL**: Configure Waafi webhook URL in merchant dashboard
4. **Static Files**: Ensure receipt templates are properly served
5. **Logging**: Configure payment logging for production

---

## Future Enhancements

1. **PDF Receipt Generation**: Implement proper PDF receipts
2. **Email Receipts**: Automatic receipt emails
3. **Refund Processing**: Handle payment refunds
4. **Multi-Payment Methods**: Support for additional payment providers
5. **Subscription Renewals**: Automatic subscription renewals
6. **Payment Analytics**: Advanced payment analytics dashboard

---

This comprehensive order history system provides everything needed for professional payment tracking and subscription management, with full Waafi integration and Somali language support. 