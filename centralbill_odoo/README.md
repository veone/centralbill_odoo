# **Web Payment Integration**

This document describes how to initiate a payment request and process the subsequent notification once it has been executed by the payer.

Integration is a quick (I promise!) 2 step process :

1. Create a payment link
2. Handle instant payment notification (IPN)

## **Environment URLs**
Name | Console | WebPay
---- | ------- | ------
Test | https://dashboard.sandbox.centralbill.app | https://pay.sandbox.centralbill.app
Production | https://dashboard.centralbill.app | https://pay.centralbill.app

## **Step 1: Create a payment link**

The payment link is a URL that displays the web payment page. The base URL to invoke for process payment depends of environment used.
Below is an example of a URL that allows you to start a payment by your customer : 

> https://pay.centralbill.app/?applicationId=fbab3ccc-719e-11ed-93ad-02420a0003c1&invoice[id]=1&invoice[customerId]=johndoe%40example.com&invoice[totalAmount][amount]=100&invoice[totalAmount][currency]=XOF&invoice[issuedAt]=2022-12-12T00%3A00%3A00%2B00%3A00&invoice[dueDate]=1970-01-01T00%3A00%3A00%2B00%3A00&description=ACME+-+Facture+%23107285&signature=9407f193b8a53f68e6184ef28cffc7a7524cff81d6e6dd76a4c624b990a3e1cf&callbackUrl=https%3A%2F%2Facme.net%2Fmodules%2Fgateways%2Fcallback%2Fcentralbill.php&redirectUrl=https%3A%2F%2Facme.net%2Fviewinvoice.php%3Fid%3D1
{.is-info}

### **URL Query Fields**

Include these fields in your URL query.

Name | Type | Description
---- | ---- | -----------
applicationId | string | The merchant application's identifier.
invoice[id] | string | The invoice's unique identifier.
invoice[customerId] | string | The customer's unique identifier.
invoice[totalAmount][amount] | float | The total amount to be paid for the invoice.
invoice[totalAmount][currency] | string | The currency of the total amount to be paid for the invoice. The currency must be in [ISO 4217](https://www.iso.org/fr/iso-4217-currency-codes.html) format.
invoice[issuedAt] | string | The date on which the invoice was issued. The date must be in [ISO 8601](https://www.iso.org/fr/iso-8601-date-and-time-format.html) format.
invoice[dueDate] | string | The date on which the invoice will be due. The date must be in [ISO 8601](https://www.iso.org/fr/iso-8601-date-and-time-format.html) format.
description | string | A description that will allow your customers to recognize the payment.
signature | string | Signing of payment.
callbackUrl (Optional) | string | The callback URL where the payment notification is sent.
redirectUrl (Optional) | string | The URL where the customer is redirected after payment.

### **Generate payment signature**

To generate a payment signature you must combine the following payment informations : `application.id`, `invoice.id`, `invoice.customerId`, `invoice.totalAmount.amount`, `invoice.totalAmount.currency` and `application.secret`.

The identifier and secret of the application can be retrieved from your administration console.

Below is an example code in [PHP](https://php.net) to generate a signature :
```php
$applicationId = 'fbab3ccc-719e-11ed-93ad-02420a0003c1';
$applicationSecret = 'app!secret';
$invoiceId = '1';
$invoiceCustomerId = 'johndoe@example.com';
$invoiceTotalAmountAmount = 1000;
$invoiceTotalAmountCurrency = 'XOF';

$signature = hash('sha256', sprintf(
    '%s,%s,%s,%s,%s,%s',
    $applicationId, 
    $invoiceId,
    $invoiceCustomerId,
    $invoiceTotalAmountAmount,
    $currency,
    $applicationSecret
));
```

## **Step 2: Handle instant payment notification (IPN)**

A payment notification is sent after each payment to a callback url configured either in your dashboard or defined in the payment link.

### **Instant Payment Notification request**

**`POST`**			`callbackUrl`			**`Instant Payment Notification method`**

#### **Response codes**

##### **Success**
Code | Reason
---- | ------
`200 - Ok` | Request was successful.
`204 - No Content` | Request was successful and has no content.

##### **Error**
Code | Reason
---- | ------
`400 - Bad Request` | Some content in the request was invalid.
`401 - Unauthorized`| User must authenticate before making a request.
`403 - Forbidden` | Policy does not allow current user to do this operation.

##### **Request parameters**
Name |  In  | Type | Description
---- | ---- | ---- | -----------
id | body | string | The transaction's unique identifier.
payment | body | Payment | The transaction's related payment.
payment.id | body | string | The payment's unique identifier.
payment.type | body | enum | The payment's type. The avalaible values are: `full` and `partial`.
payment.application | body | object | The payment's application identifier. 
payment.invoice | body | Invoice | The payment's invoice.
payment.extras | body | object | The payment's extra data.
payment.totalAmountAlreadyPaid | body | float | The payment total amount already paid.
invoice | body | Invoice | The information of the invoice paid.
invoice.id | body | string | The invoice's unique identifier.
invoice.customerId | body | string | The customer's unique identifier.
invoice.totalAmount.amount | body | float | The total amount paid for the invoice.
invoice.totalAmount.currency | body | string | The currency of the total amount paid for the invoice. The currency must be in [ISO 4217](https://www.iso.org/fr/iso-4217-currency-codes.html) format.
invoice.issuedAt | body | string | The date on which the invoice was issued. The date must be in [ISO 8601](https://www.iso.org/fr/iso-8601-date-and-time-format.html) format.
invoice.dueDate | body | string | The date on which the invoice will be due. The date must be in [ISO 8601](https://www.iso.org/fr/iso-8601-date-and-time-format.html) format.
paymentFee.amount | body | float | The amount of payment fees applied to the transaction.
paymentFee.currency | body | string | The currency of payment fees applied to the transaction. The currency must be in [ISO 4217](https://www.iso.org/fr/iso-4217-currency-codes.html) format.
externalTransactionId | body | string | The transaction external identifier provide by payment processor.
result | body | object | The transaction's result.
result.origin | body | object | The transaction's result originator.
result.status | body | enum | The transaction's result status. The avalaible values are: `COMPLETED`, `NEEDS_MERCHANT_VALIDATION`, `CANCELED`, `REFUSED`, `FAILED`, and `REVERSED`.
result.statusReason | body | string | The transaction's result status reason.
Authorization | header | string | The request is secured by the HTTP Signature Authentication protocol.
Content-Type | header | string | Set the MIME type for the request.

###### **Request example with password authentication**

```
curl -X POST -i 'callbackUrl' \
-H 'Host: acme.org' \
-H 'Content-Type: application/json' \
-H 'Date: Thu, 01 Dec 2022 19:08:22 +0000' \
-H 'Digest: SHA-256=NjQzMWNjYWMwNjdkYTA5ZWFiZTJiZDMyMDU3NmQxOWEyM2RmNTYyMzMyMDcyOTliMTJmMzAxYjY1ZDZkOTYzMg==' \
-H 'Signature: keyId="fbab3ccc-719e-11ed-93ad-02420a0003c1",algorithm="hmac-sha256",headers="(request-target) content-type date digest",signature="fiFBCK8NWWhvk6fJul8ezzpVXSh9q30VRO8qn3XGxTQ="' \
-H 'Authorization: Signature keyId="2bc56634-673c-11ed-acf4-0242ac13000e",algorithm="hmac-sha256",headers="(request-target) content-type date digest",signature="fiFBCK8NWWhvk6fJul8ezzpVXSh9q30VRO8qn3XGxTQ="' \
-d '{
    "id": "63a368858622d5ded108e4b3",
    "payment": {
        "id": "63a368858622d5ded108e4b2",
        "type": "full",
        "application": {
            "id": "b3695b9c-816b-11ed-8083-32706358435f",
            "name": "banking"
        },
        "invoice": {
            "id": "1",
            "customerId": "1",
            "totalAmount": {
                "amount": 1000,
                "currency": "XOF"
            },
            "issuedAt": "2022-12-21T20:11:49+00:00"
        },
        "extras": [],
        "totalAmountAlreadyPaid": {
            "amount": 1000,
            "currency": "XOF"
        }
    },
    "invoice": {
        "id": "1",
        "customerId": "1",
        "totalAmount": {
            "amount": 1000,
            "currency": "XOF"
        },
        "issuedAt": "2022-12-21T20:11:49+00:00"
    },
    "paymentFee": {
        "amount": 0,
        "currency": "XOF"
    },
    "id": "63a368858622d5ded108e4b3",
    "result": {
        "origin": "processor",
        "status": "COMPLETED"
    }
}'
```

### **How validate Payment Notification request?**

The Instant Payment Notification (IPN) request is secured from HTTP Signature Authentication.
Below is an example code in [PHP](https://php.net) to handle payment notification request :

```php
// Fetch application secret configuration parameters.
$applicationSecret = 'app!secret';

$body = json_decode(file_get_contents('php://input'), true);
$transactionId = $body['id'];
$transactionStatus = $body['result']['status'];
$invoiceId = $body['invoice']['id'];
$invoiceTotalAmount = $body['invoice']['totalAmount']['amount'];
$paymentFee = $body['paymentFee']['amount'];

/**
 * Validate callback authenticity.
 */
$components = [];
$headers = array_change_key_case(getallheaders(), \CASE_LOWER);

foreach (explode(',', $headers['signature'] ?? '') as $value) {
    if (!$component = explode('=', $value, 2)) {
        continue;
    }

    $components[$component[0]] = trim($component[1], '"');
}

if (array_diff(['keyId', 'algorithm', 'headers', 'signature'], array_keys($components))) {
    die('Payment failed');
}

if ('hmac-sha256' !== $components['algorithm']) {
    die('Payment failed');
} 

$signature = [];

foreach (explode(' ', strtolower($components['headers'])) as $header) {
    $signature[] = sprintf('%s: %s', $header, '(request-target)' !== $header ? $headers[$header] : sprintf('%s %s', strtolower($_SERVER['REQUEST_METHOD']), $_SERVER['REQUEST_URI']));
}
        
if (false === hash_equals(base64_encode(hash_hmac('sha256', implode(\PHP_EOL, $signature), applicationSecret, true)), $components['signature'])) {
    die('Payment failed');
}

/**
 * Validate transaction status.
 */
if ('COMPLETED' !== transactionStatus) {
    die('Payment failed');
}

// Busines Logic here
// ...
```

### **Transaction Status**

The transaction status value and description

Value | Description
---- | ------
`PENDING` | We’re reviewing the transaction. We’ll send your payment to the recipient after your payment source has been verified.
`PROCESSING`| We’re processing your payment and the transaction should be completed shortly.
`CANCELED` | You canceled your payment, and the money was credited back to your account.
`COMPLETED` | The transaction was successful and the money is in the recipient’s account.
`REFUSED` | The recipient didn’t receive your payment. If you still want to make your payment, we recommend that you try again.
`FAILED` | Your payment didn’t go through. We recommend that you try your payment again.
`REVERSED` | Either you canceled the transaction or we did.
`NEEDS_MERCHANT_VALIDATION` | Either you awaiting merchant validation.