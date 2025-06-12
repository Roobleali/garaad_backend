Introduction
Welcome to the WaafiPay Ecommerce Payment Gateway

WaafiPay
WaafiPay is the leading payment gateway in East Africa, we offer a comprehensive solution for merchants to seamlessly accept payments from customers using cards, mobile wallets, and bank accounts. Designed with the flexibility to cater to a diverse marketplace, our API enables businesses to expand their reach and facilitate smoother transactions across different payment platforms.

WaafiPay is committed to providing a secure transaction environment and is fully compliant with the Payment Card Industry Data Security Standard (PCI DSS). This ensures that every transaction is processed with the highest level of security, safeguarding merchant and customer data against fraud and breaches.

By integrating with WaafiPay, merchants gain a competitive edge with the ability to process payments through popular mobile wallets like WAAFI, ZAAD, EVCPlus, and SAHAL, alongside direct Card and Bank Account transactions. This versatility makes WaafiPay an ideal partner for businesses looking to enhance their payment systems, improve customer satisfaction, and increase sales efficiency in the dynamic East African market.

Whether you are integrating WaafiPay into a mobile app, a web store, or a custom-built e-commerce solution, our documentation will guide you through the necessary steps and technical details. It includes detailed descriptions of our API endpoints, data formats, and operational procedures, along with code examples in multiple programming languages to assist you in a smooth integration process. Whether you're a small business, a large enterprise, or a freelance developer, Waafipay provides the flexibility and functionality you need to manage payments efficiently and securely.

Setup
API Access: You must have a valid Waafipay account. If you do not have one, please visit WAAFI HQ Offices (Telesom, Zaad, Golis, WAAFI SAB) to register in person. Once registered, you will receive your API credentials, including an API key and a client ID, which are necessary for authentication.
Secure Environment: Ensure that your development and production environments comply with our security standards, which include using HTTPS to encrypt all API requests to safeguard sensitive data.
Compatibility Check: Your system should be compatible with our API specifications. We support JSON for request and response bodies, and our API can be accessed from any platform that supports HTTPS requests.
Development Tools: You should have the necessary development tools installed, including a REST client for testing API requests, and an environment for writing and testing your integration code.
By meeting these requirements, you will be ready to proceed with integrating the WaafiPay API and start processing payments securely and efficiently through Mobile Wallets and Bank Accounts.
Introduction
Our API (Application Programming Interface) enables client applications to securely communicate with WaafiPay servers using a predefined message format. The structure of our API responses includes key fields that facilitate this communication:

channelName: Indicates the request origin, such as WEB, which helps differentiate between various channels.

serviceName: Defines the requested operation, including:

API_PURCHASE
API_CANCELPURCHASE
API_PREAUTHORIZE
API_PREAUTHORIZE_COMMIT
API_PREAUTHORIZE_CANCEL
This allows clear identification of the specific action being requested.

serviceParams: Common parameters within this section include:

merchantUid, apiUserId, and apiKey: Authenticate and link requests to the appropriate merchant and API user.
paymentMethod: Specifies the type of payment, such as MWALLET_ACCOUNT (payments from Wallet Accounts such as EVC or ZAAD) or MWALLET_BANKACCOUNT (from bank account).
referenceId and description: Provide tracking and context for transactions, ensuring consistency across related operations.
The referenceId parameter is a unique identifier provided by the merchant’s system. It represents the order ID or transaction ID associated with the transaction. This ID ensures accurate tracking and referencing of the transaction within the merchant’s records and is designed to be unique within the payment system to prevent any duplicate transactions.

referenceId must only contain alphanumeric, dash, underscore and dot characters
Decimal Precision Policy
We accept amounts with up to two decimal places for all transactions. This includes both whole numbers and decimal values.

If a value has more than two decimal places, it will be automatically truncated (not rounded) to two decimal places during processing.

✅ Valid Examples:
10 (no decimal places)
10.2 (one decimal place)
10.23 (two decimal places)
🔄 Automatically Truncated:
10.237 → 10.23
99.999 → 99.99
Note: The amount used after truncation will be returned in the API response. Make sure to rely on this value for reconciliation and display purposes.

We recommend rounding or truncating the amount before submitting a transaction to ensure consistency and prevent unexpected discrepancies between submitted and processed values.

API Endpoint
Testing Environment: http://sandbox.waafipay.net/asm
Production Environment: https://api.waafipay.com/asm
Our API is available in various programming languages, enabling easy integration into a merchant's existing website or application. This structured approach ensures that each request is secure, identifiable, and traceable through a standardized framework.

Response Codes
2001 RCS_SUCCESS: Request/Transaction is approved/successful
5301 RCS_INVALID_HPPKEY: Transaction cannot be performed due to wrong hpp key
5302 RCS_INVALID_HPPTOKEN: Transaction cannot be performed due to wrong hpp Token
5303 RCS_INVALID_HPPRESULTTOKEN: Transaction cannot be performed due to wrong hpp Token result
5304 RCS_HPP_MERCHANT_REFERENCEID_MISMATCH: Transaction cannot be performed due to mismatch of Transaction Reference
5305 RCS_HPP_REQUESTID_MISMATCH: Transaction cannot be performed due to mismatch of Transaction RequestId
5306 RCS_HPP_USERACTION_CANCELLED: User cancelled the transaction
5307 RCS_HPPTOKEN_EXPIRED: Transaction cannot be performed due to Token expired
5308 RCS_HPP_SUBSCRIPTION_ISNOT_ENABLED: Merchant is not allowed for this service type
5309 RCS_HPP_USERACTION_TIMEOUT: User didn't process the transaction in 5 minutes
Purchase
The WaafiPay API supports multiple payment actions through a unified endpoint. For Purchase actions, use the serviceName parameter with different values to initiate a purchase, cancel a purchase, or refund a purchase.

1. Purchase
serviceName: API_PURCHASE
Purpose: Charges the payer's account, completing the payment.
Request Example: Set serviceName to API_PURCHASE and customize payerInfo and transactionInfo as required.
Request Structure

POST /asm
{
    "schemaVersion": "1.0",
    "requestId": "{{$guid}}",
    "timestamp": "{{$timestamp}}",
    "channelName": "WEB",
    "serviceName": "API_PURCHASE",
    "serviceParams": {
        "merchantUid": {{MERCHANT_UID}},
        "apiUserId": {{API_USER_ID}},
        "apiKey": {{API_KEY}},
        "paymentMethod": "MWALLET_ACCOUNT",
        "payerInfo": {
            "accountNo": "25261111111"
        },
        "transactionInfo": {
            "referenceId": "{{$randomBankAccount}}",
            "invoiceId": "154",
            "amount": "10",
            "currency": "USD",
            "description": "{{$randomLoremSentence}}"
        }
    }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., API_PURCHASE)
merchantUid	String	7-15	Required	Unique merchant identifier
apiUserId	String	7-15	Required	API user identifier for the merchant
apiKey	String	20-40	Required	API key for request authentication
paymentMethod	String	5-20	Required	Payment method being used (e.g., MWALLET_ACCOUNT)
payerInfo.accountNo	String	10-20	Required	Account number of the payer
transactionInfo.referenceId	String	1-50	Required	Reference ID for the transaction
transactionInfo.invoiceId	String	1-50	Required	Invoice ID
transactionInfo.amount	Number	N/A	Required	Transaction amount (numeric)
transactionInfo.currency	String	3	Required	Currency code (e.g., "USD")
transactionInfo.description	String	0-255	Optional	Description of the transaction (e.g., random sentence)
Response Structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 09:04:44.741",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "accountNo": "252611****1111",
    "accountType": "MWALLET_ACCOUNT",
    "state": "APPROVED",
    "merchantCharges": "0.1",
    "referenceId": "1234",
    "transactionId": "1268666",
    "issuerTransactionId": "ISR0011268666",
    "txAmount": "10.0"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.accountNo	String	10-20	Account number of the payer
params.accountType	String	5-20	Type of the account (e.g., "MWALLET_ACCOUNT")
params.state	String	1-15	State of the transaction (e.g., "APPROVED")
params.merchantCharges	Number	N/A	Merchant charges (numeric)
params.referenceId	String	1-50	Reference ID for the transaction
params.transactionId	String	1-50	Transaction ID returned from the transaction
params.issuerTransactionId	String	1-50	Issuer transaction ID
params.txAmount	Number	N/A	Amount for the transaction (numeric)
2.Purchase Reversal
serviceName: API_CANCELPURCHASE
Purpose: Reverses the payment for a previously completed purchase.
Request Example: Set serviceName to API_CANCELPURCHASE and include the transactionId and referenceId of the original transaction.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$randomUUID}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "API_CANCELPURCHASE",
  "serviceParams": {
    "merchantUid": {{MERCHANT_UID}},
    "apiUserId": {{API_USER_ID}},
    "apiKey": {{API_KEY}},
    "paymentMethod": "MWALLET_ACCOUNT",
    "transactionId": "{{transactionId}}",
    "referenceId": "{{referenceId}}",
    "description": "Cancelled"
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., API_CANCELPURCHASE)
merchantUid	String	7-15	Required	Unique merchant identifier
apiUserId	String	7-15	Required	API user identifier for the merchant
apiKey	String	20-40	Required	API key for request authentication
paymentMethod	String	5-20	Required	Payment method being used (e.g., MWALLET_ACCOUNT)
transactionId	String	1-50	Required	Original Transaction ID from previous purchase
referenceId	String	1-50	Optional	Reference ID for the transaction
description	String	0-255	Optional	Description of the action (e.g., "Cancelled")
Response Structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 09:07:48.786",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "description": "success",
    "state": "approved",
    "transactionId": "1268667",
    "referenceId": "1234"
  }
}
Purchase Reversal Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.description	String	0-255	Description of the response (e.g., "success")
params.state	String	1-15	State of the transaction (e.g., "approved")
params.transactionId	String	1-50	Transaction ID returned from the transaction
params.referenceId	String	1-50	Reference ID returned from the transaction
Summary:
Request Key Parameters: Includes details for canceling the purchase, such as transactionId, referenceId, and the cancellation description (e.g., "Cancelled").
Response Key Parameters: Contains the result of the cancellation, including transaction status (approved), description, and the associated transaction IDs.


PreAuthorization
The WaafiPay API allows for managing preauthorized transactions through a single endpoint, utilizing different values in the serviceName parameter to perform specific actions: Preauthorization, Cancellation, and Commitment of transactions.

Actions
1. PreAuthorization
serviceName: API_PREAUTHORIZE
Purpose: Reserves funds for a specific amount on a user’s account without immediately charging.
Request Example:Set serviceName to API_PREAUTHORIZE and customize the payerInfo and transactionInfo as required.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$guid}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "API_PREAUTHORIZE",
  "serviceParams": {
    "merchantUid": "{{MERCHANT_UID}}",
    "apiUserId": {{API_USER_ID}},
    "apiKey": "{{API_KEY}}",
    "paymentMethod": "MWALLET_ACCOUNT",
    "payerInfo": {
      "accountNo": "25261111111"
    },
    "transactionInfo": {
      "referenceId": "{{$randomBankAccount}}",
      "invoiceId": "INV99222255",
      "amount": "1",
      "currency": "USD",
      "description": "test preauth"
    }
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	5-20	Constant	Channel of the request (e.g., "WEB")
serviceName	String	15-25	Constant	The name of the service being called
merchantUid	String	7-15	Required	Unique merchant identifier
apiUserId	String	7-15	Required	API user identifier for the merchant
apiKey	String	20-40	Required	API key for request authentication
payerInfo.accountNo	String	10-20	Required	Account number of the payer
paymentMethod	String	5-20	Required	Payment method being used (e.g., MWALLET_ACCOUNT)
transactionInfo.amount	Number	N/A	Required	Transaction amount (numeric)
transactionInfo.currency	String	3	Required	Currency code (e.g., "USD")
transactionInfo.referenceId	String	10-30	Required	Unique reference ID for the transaction
transactionInfo.invoiceId	String	10-30	Optional	Invoice identifier
transactionInfo.description	String	5-100	Optional	Description of the transaction
Response structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 08:52:06.287",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "state": "APPROVED",
    "referenceId": "1234",
    "transactionId": "1268664",
    "txAmount": "1.0"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.state	String	1-15	State of the transaction (e.g., "APPROVED")
params.referenceId	String	1-50	Reference ID returned from the transaction
params.transactionId	String	1-50	Transaction ID returned from the transaction
params.txAmount	Number	N/A	Amount for the transaction (numeric)
Summary:
Request Parameters: Identifiers for the transaction and the user, including service details, payment method, and the amount.
Response Parameters: The result of the transaction, including the response code, message, and transaction state.
2. Cancellation
serviceName: API_PREAUTHORIZE_CANCEL
Purpose: Cancels a previously preauthorized transaction, releasing the reserved funds.
Request Example: Set serviceName to API_PREAUTHORIZE and customize the payerInfo and transactionInfo as required.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$guid}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "API_PREAUTHORIZE",
  "serviceParams": {
    "merchantUid": "{{MERCHANT_UID}}",
    "apiUserId": {{API_USER_ID}},
    "apiKey": "{{API_KEY}}",
    "paymentMethod": "MWALLET_ACCOUNT",
    "payerInfo": {
      "accountNo": "25261111111"
    },
    "transactionInfo": {
      "referenceId": "{{$randomBankAccount}}",
      "invoiceId": "INV99222255",
      "amount": "1",
      "currency": "USD",
      "description": "test preauth"
    }
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., API_PREAUTHORIZE_CANCEL)
merchantUid	String	7-15	Required	Unique merchant identifier
apiUserId	String	7-15	Required	API user identifier for the merchant
apiKey	String	20-40	Required	API key for request authentication
referenceId	String	1-50	Required	Reference ID for the transaction
transactionId	String	1-50	Required	Transaction ID
description	String	0-255	Optional	Description of the action (e.g., "Booking order canceled")
Response

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 08:59:59.986",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "description": "success",
    "state": "approved",
    "transactionId": "1268665",
    "referenceId": "1234"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.description	String	0-255	Description of the response (e.g., "success")
params.state	String	1-15	State of the transaction (e.g., "approved")
params.transactionId	String	1-50	Transaction ID returned from the transaction
params.referenceId	String	1-50	Reference ID returned from the transaction
Summary:
Request Parameters: Includes details for the transaction cancelation request such as referenceId, transactionId, and description (e.g., cancelation description).
Response Parameters: Contains status information about the response, including the transaction state (approved), description, and transaction IDs.
3. Commit
serviceName: API_PREAUTHORIZE_COMMIT
Purpose: Finalizes a previously preauthorized transaction, confirming the reserved funds.
Request Example: Set serviceName to API_PREAUTHORIZE_COMMIT and include the referenceId and transactionId.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$randomUUID}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "API_PREAUTHORIZE_COMMIT",
  "serviceParams": {
    "merchantUid": {{MERCHANT_UID}},
    "apiUserId": {{API_USER_ID}},
    "apiKey": {{API_KEY}},
    "referenceId": "{{referenceId}}",
    "transactionId": "{{transactionId}}",
    "description": "PREAUTH Commited"
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., API_PREAUTHORIZE_COMMIT)
merchantUid	String	7-15	Required	Unique merchant identifier
apiUserId	String	7-15	Required	API user identifier for the merchant
apiKey	String	20-40	Required	API key for request authentication
referenceId	String	1-50	Required	Reference ID for the transaction
transactionId	String	1-50	Required	Transaction ID
description	String	0-255	Optional	Description of the action (e.g., "PREAUTH Committed")
Response Structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 08:55:45.828",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "description": "success",
    "state": "approved",
    "transactionId": "1268664",
    "referenceId": "1234"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.description	String	0-255	Description of the response (e.g., "success")
params.state	String	1-15	State of the transaction (e.g., "approved")
params.transactionId	String	1-50	Transaction ID returned from the transaction
params.referenceId	String	1-50	Reference ID returned from the transaction
Summary:
Request Key Parameters: Includes details for committing the preauthorization, such as referenceId, transactionId, and a description of the action
Response Key Parameters: Contains the result of the commit action, including the state (approved), description, and transaction identifiers.

Hosted Payment Page
WaafiPay provides a Hosted Payment Page (HPP) for handling purchases, refunds, and transaction inquiries through a secure, web-based interface. Use the serviceName parameter to specify the action for each transaction.

1. Initiate Purchase
serviceName: HPP_PURCHASE
Purpose: Redirects customers to a secure HPP to complete their transaction.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$randomUUID}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "HPP_PURCHASE",
    "serviceParams": {
    "merchantUid": "{{MERCHANT_UID}}",
    "storeId": {{STORE_ID}},
	  "hppKey": "{{HPP_KEY}}",
    "paymentMethod": "CREDIT_CARD",
    "hppSuccessCallbackUrl": "http://localhost:3000/api/hpp/success",
    "hppFailureCallbackUrl": "http://localhost:3000/api/hpp/failure",
    "hppRespDataFormat": 4,
    "transactionInfo": {
      "referenceId": "WS_{{$randomBankAccount}}",
      "invoiceId": "WS_{{$randomBankAccount}}",
      "amount": 10,
      "currency": "EUR",
      "description": "payment"
    }
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., HPP_PURCHASE)
merchantUid	String	7-15	Required	Unique merchant identifier
storeId	Number	N/A	Required	The store ID where the purchase is made
hppKey	String	20-40	Required	HPP key for secure purchase initiation
paymentMethod	String	5-20	Required	Payment method being used (e.g., CREDIT_CARD)
hppSuccessCallbackUrl	String	0-255	Required	URL for success callback from the HPP system
hppFailureCallbackUrl	String	0-255	Required	URL for failure callback from the HPP system
hppRespDataFormat	Number	1-3	Required	Response data format for the HPP system
transactionInfo.referenceId	String	1-50	Required	Reference ID for the transaction
transactionInfo.invoiceId	String	1-50	Required	Invoice ID for the transaction
transactionInfo.amount	Number	N/A	Required	Transaction amount (numeric)
transactionInfo.currency	String	3	Required	Currency code (e.g., "EUR")
transactionInfo.description	String	0-255	Optional	Description of the transaction (e.g., "payment")
Response Structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 09:19:10.131",
  "responseId": "12314",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "hppUrl": "https://sandbox.waafipay.net/hpp/token/4542676573566A5261366B6A485049715056534A45773D3D",
    "directPaymentLink": "https://sandbox.waafipay.net/hpp/token/4542676573566A5261366B6A485049715056534A45773D3D?r=10629",
    "orderId": "1185941",
    "hppRequestId": "10629",
    "referenceId": "WS_123"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.hppUrl	String	0-255	URL for the HPP page (to process the payment)
params.directPaymentLink	String	0-255	Direct link for processing the payment
params.orderId	String	1-50	Order ID for the transaction
params.hppRequestId	String	1-50	HPP request ID
params.referenceId	String	1-50	Reference ID for the transaction
Summary:
Request Key Parameters: Includes details for initiating an HPP purchase, such as paymentMethod, hppSuccessCallbackUrl, transactionInfo.referenceId, and transactionInfo.amount.
Response Key Parameters: Contains the result of the purchase request, including the URLs for the HPP page (hppUrl, directPaymentLink), the order details (orderId, hppRequestId), and the referenceId of the transaction.
2. Refund Purchase
serviceName: HPP_REFUNDPURCHASE
Purpose: Processes a refund for a previously completed transaction.
Request Structure

POST /asm
{
  "schemaVersion": "1.0",
  "requestId": "{{$randomUUID}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "HPP_REFUNDPURCHASE",
  "serviceParams": {
    "merchantUid": "{{MERCHANT_UID}}",
    "storeId": {{STORE_ID}},
    "hppKey": "{{HPP_KEY}}",
    "amount": "10",
    "transactionId": 1255515,
    "description": "Hpp refund"
  }
}
Refund Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., HPP_REFUNDPURCHASE)
merchantUid	String	7-15	Required	Unique merchant identifier
storeId	String	7-15	Required	Store ID associated with the refund
hppKey	String	20-40	Required	HPP key for secure refund initiation
amount	Number	N/A	Required	Refund amount (numeric)
transactionId	Number	N/A	Required	Transaction ID being refunded
description	String	0-255	Optional	Description of the refund request (e.g., "Hpp refund")
Refund Response Structure

{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 09:24:48.347",
  "responseId": "12314",
  "responseCode": "5202",
  "errorCode": "E10207",
  "responseMsg": "RCS_TRAN_ALREADY_CANCELLED",
  "params": {}
}
Refund Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "E10207" for an error)
responseMsg	String	0-255	Human-readable message for the response
params	Object	N/A	Empty object, as there is no further data in this response
Summary:
Request Key Parameters: Includes details for initiating an HPP refund, such as amount, transactionId, and a description (e.g., "Hpp refund").
Response Key Parameters: Contains the result of the refund request, including an error code (E10207), message (RCS_TRAN_ALREADY_CANCELLED), and an empty params object indicating no additional data.
3. Retrieve Transaction Information
serviceName: HPP_GETTRANINFO
Purpose: Fetches transaction details for a specific transaction.
Request Structure

{
  "schemaVersion": "1.0",
  "requestId": "{{$randomUUID}}",
  "timestamp": "{{$timestamp}}",
  "channelName": "WEB",
  "serviceName": "HPP_GETTRANINFO",
  "serviceParams": {
      "merchantUid": {{MERCHANT_UID}},
      "storeId": {{STORE_ID}},
      "hppKey": {{HPP_KEY}},
      "referenceId": "WS:6671753970"
  }
}
Request Parameters
Parameter	Data Type	Length	Presence	Description
schemaVersion	String	5	Constant	API schema version (e.g., "1.0")
requestId	String	36 (UUID)	Required	Unique request identifier (e.g., UUID)
timestamp	String	20	Required	Date and time of the request
channelName	String	3-10	Constant	The channel through which the request was made
serviceName	String	15-25	Constant	The name of the service being called (e.g., HPP_GETTRANINFO)
merchantUid	String	7-15	Required	Unique merchant identifier
storeId	String	7-15	Required	Store ID associated with the transaction
hppKey	String	20-40	Required	HPP key for secure transaction information fetch
referenceId	String	1-50	Required	Reference ID for the transaction
Response Structure

POST /asm
{
  "schemaVersion": "1.0",
  "timestamp": "2024-11-05 12:19:05.05",
  "responseId": "123114",
  "responseCode": "2001",
  "errorCode": "0",
  "responseMsg": "RCS_SUCCESS",
  "params": {
    "tranStatusDesc": "Approved",
    "amount": "2.0",
    "payerId": "252700000000",
    "paymentMethod": "mwallet_account",
    "description": "payment",
    "tranDate": "2024-11-05 10:58:50.0",
    "currency": "USD",
    "invoiceId": "16F7F28E21EC",
    "tranAmount": "2.0",
    "transactionId": "126895",
    "tranStatusId": "3",
    "status": "Approved"
  }
}
Response Parameters
Parameter	Data Type	Length	Description
schemaVersion	String	5	API schema version (e.g., "1.0")
timestamp	String	20	Date and time of the response
responseId	String	1-50	Unique response identifier
responseCode	String	1-10	Response code indicating the result of the request
errorCode	String	1-5	Error code (e.g., "0" for no error)
responseMsg	String	0-255	Human-readable message for the response
params.tranStatusDesc	String	0-255	Description of the transaction status (e.g., "Approved")
params.amount	Number	N/A	Amount of the transaction
params.payerId	String	1-50	Payer's unique identifier
params.paymentMethod	String	1-50	Payment method used (e.g., "mwallet_account")
params.description	String	0-255	Description of the transaction (e.g., "payment")
params.tranDate	String	20	Date and time of the transaction
params.currency	String	3	Currency code (e.g., "USD")
params.invoiceId	String	1-50	Invoice ID for the transaction
params.tranAmount	Number	N/A	Amount of the transaction
params.transactionId	String	1-50	Transaction ID
params.tranStatusId	String	1-10	Status ID of the transaction
params.status	String	0-255	Status of the transaction (e.g., "Approved")
Summary:
Request Key Parameters: Includes details for fetching transaction information, such as referenceId, merchantUid, and hppKey.
Response Key Parameters: Contains detailed transaction information, including tranStatusDesc (e.g., "Approved"), payerId, amount, transactionId, and other transaction-specific details such as currency, status, and invoiceId.

Webhooks
WaafiPay offers webhook notifications to keep you informed about transaction status updates. A webhook is an HTTP callback that automatically sends real-time data to a pre-configured URL when specific events occur, such as the completion or failure of a transaction. This enables your system to immediately receive and process updates without the need for constant polling. Please note that webhook notifications are currently supported only for transactions processed via the Hosted Payment Page (HPP), and failed webhook deliveries do not trigger automatic retry attempts.

Merchants can register their webhook endpoints via our API, receiving real-time updates about transaction outcomes, including both successful completions and failures. To ensure robust integration, it is recommended to implement proper logging and error-handling mechanisms for webhook events on your end. This is especially important to prevent missing crucial information due to issues like failed customer redirection (such as HPP callbacks).

If you need any help with integration or have further questions, feel free to reach out. We're here to help!

1. Register a Webhook
You can only register one webhook URL to receive payment notifications. The provided URL should be publicly accessible.

In all API requests, you must include the HPP credentials: merchantUid, storeId, hppKey.

Request:

POST /asm
{
    "schemaVersion": "1.0",
    "requestId": "{{$guid}}",
    "timestamp": "{{$timestamp}}",
    "channelName": "WEB",
    "serviceName": "WEBHOOK_REGISTER",
    "serviceParams": {
        "merchantUid": {{MERCHANT_UID}},
        "storeId": {{STORE_ID}},
        "hppKey": {{HPP_KEY}},
        "url": "https://api.example.com/webhook",
        "description": "a description"
    }
}
Request Parameters
Parameter	Data Type	Presence	Description
schemaVersion	String	Constant	API schema version (e.g., "1.0").
requestId	UUID String	Required	Unique request identifier (e.g., UUID).
timestamp	String	Required	Date and time of the request.
channelName	String	Constant	The channel through which the request was made.
serviceName	String	Constant	The name of the service being called (e.g., WEBHOOK_REGISTER).
merchantUid	String	Required	Unique merchant identifier.
storeId	String	Required	API store/user identifier for the merchant.
hppKey	String	Required	API key for request authentication.
partnerUid	String	Optional	WAAFI Merchant Number (PartnerUID).
description	String	Optional	Description of your webhook usage.
url	String	Required	URL for webhook to be sent to. Only one webhook endpoint is allowed per merchant.
Response:

{
    "schemaVersion": "1.0",
    "timestamp": "2024-02-08 04:38:42.938",
    "responseId": "{{$guid}}",
    "responseCode": "2001",
    "errorCode": "0",
    "responseMsg": "Webhook created successfully",
}
2. Get All Webhooks
Retrieve a list of all existing webhooks.

POST Request


POST /asm
{
    "schemaVersion": "1.0",
    "requestId": "{{$guid}}",
    "timestamp": "{{$timestamp}}",
    "channelName": "WEB",
    "serviceName": "WEBHOOK_LIST",
    "serviceParams": {
        "merchantUid": "{{MERCHANT_UID}}",
        "storeId": {{STORE_ID}},
        "hppKey": "{{HPP_KEY}}",
    }
}
Response


{
    "params": {
        "data": [
            {
                "id": "25",
                "url": "https://app.sample.com/webhook",
                "description": "testing",
                "merchantId": "10165",
                "partnerUid": "400394",
                "merchantName": "WaafiPay Store"
            }
        ]
    }
}
3. Update Webhook
You can update the url and description properties of an existing webhook.

POST Request


POST /asm
{
    "schemaVersion": "1.0",
    "requestId": "{{$guid}}",
    "timestamp": "{{$timestamp}}",
    "channelName": "WEB",
    "serviceName": "WEBHOOK_UPDATE",
    "serviceParams": {
        "merchantUid": "{{MERCHANT_UID}}",
        "storeId": {{STORE_ID}},
        "hppKey": "{{HPP_KEY}}",
        "url": "https://api.sample.so/webhook/v2",
        "webhookId": 10,
        "description": "another description"
    }
}
4. Delete Webhook
Remove an existing webhook.

POST Request


POST /asm
{
    "schemaVersion": "1.0",
    "requestId": "{{$guid}}",
    "timestamp": "{{$timestamp}}",
    "channelName": "WEB",
    "serviceName": "WEBHOOK_DELETE",
    "serviceParams": {
        "merchantUid": "{{MERCHANT_UID}}",
        "storeId": {{STORE_ID}},
        "hppKey": "{{HPP_KEY}}",
        "webhookId": 10,
    }
}
Receiving a Webhook on Your Server
Once registered, your webhook URL will receive transaction notifications in the following format:

Webhook Sample Payload


{
    "customerNumber": "252613282000",
    "customerName": "Mohamed Abdullahi Abdi",
    "partnerUID": "${MERCHANT_UID}",
    "transferInfo": {
        "amount": "10",
        "charges": "0",
        "transferId": "176329573",
        "transferCode": "1017635883",
        "transactionDate": "08/02/23 19:15:38",
        "transferStatus": "3",
        "currencySymbol": "$",
        "referenceId": "1001",
        "currencyCode": "840",
        "currencyName": "UNITED STATES-US Dollar",
        "paymentChannel": "MOBILEAPP",
        "description": "Invoice No: 1001",
        "tokenReferenceId": "223"
    }
}
Please ensure your server is properly configured to handle these notifications to keep your system up-to-date with transaction statuses.