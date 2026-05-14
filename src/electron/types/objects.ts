export type Order = {
  id: string;
  client: string;
  date: string;
  price: string;
}

export type Product = {
  quantity: number;
  code: string;
  description: string;
  price: string;
  isRegistered: boolean;
  brandFull: string;
  brandShort: string;
}

export type OrderData = {
  orderNumber: string;
  products: Product[];
  shippingTax: string;
  clientVAT: string;
  clientName: string;
}