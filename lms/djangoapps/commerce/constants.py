""" Constants for this app as well as the external API. """


class OrderStatus(object):
    """Constants representing all known order statuses. """
    OPEN = 'Open'
    ORDER_CANCELLED = 'Order Cancelled'
    BEING_PROCESSED = 'Being Processed'
    PAYMENT_CANCELLED = 'Payment Cancelled'
    PAID = 'Paid'
    FULFILLMENT_ERROR = 'Fulfillment Error'
    COMPLETE = 'Complete'
    REFUNDED = 'Refunded'
