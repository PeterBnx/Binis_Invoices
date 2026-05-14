import { Order, OrderData } from "./objects.ts";

export {};

declare global {
  interface Window {
    api: IpcApi;
  }

  interface IpcApi {
    send: <K extends keyof IpcSendChannels>(channel: K, data: IpcSendChannels[K]) => void;
    receive: <K extends keyof IpcReceiveChannels>(channel: K, callback: (...args: IpcReceiveChannels[K]) => void) => void;
    invoke: <K extends keyof IpcInvokeChannels>(channel: K, data?: IpcInvokeChannels[K]['args']) => Promise<IpcInvokeChannels[K]['return']>;
  }

  // Messages sent from renderer to main (fire and forget)
  interface IpcSendChannels {
    run_python_script: string;
  };

  // Messages received in renderer from main (via send)
  interface IpcReceiveChannels {
    message_from_client: [message];
    socket_message: [message];
  };

  // Messages from renderer expecting a response (invoke/handle)
  interface IpcInvokeChannels {
    get_orders: {
      args: void;
      return: Order[];
    },

    get_order_data: {
      args: string[];
      return: OrderData;
    }

    register_products: {
      args: string;
      return: string;
    }

    extract_invoice: {
      args: string;
      return: string;
    }

    // WEBSOCKET CONNECTION
    start_server_connection: {
      args: void;
      return: boolean;
    },
    stop_server_connection: {
      args: void;
      return: boolean;
    },

    // UTILS
    are_objects_different: {
      args: [object, object];
      return: boolean;
    },
  
  };

}
