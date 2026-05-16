import { Order, OrderData } from "./objects.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type message = any; 

declare global {
  interface ImportMetaEnv {
    readonly VITE_SUPABASE_URL: string;
    readonly VITE_SUPABASE_ANON_KEY: string; // Fixed name to match client
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }

  interface Window {
    api: IpcApi;
  }

  interface IpcApi {
    send: <K extends keyof IpcSendChannels>(channel: K, data: IpcSendChannels[K]) => void;
    receive: <K extends keyof IpcReceiveChannels>(channel: K, callback: (...args: IpcReceiveChannels[K]) => void) => void;
    invoke: <K extends keyof IpcInvokeChannels>(channel: K, data?: IpcInvokeChannels[K]['args']) => Promise<IpcInvokeChannels[K]['return']>;
  }

  interface IpcSendChannels {
    run_python_script: string;
  }

  interface IpcReceiveChannels {
    message_from_client: [message];
    socket_message: [message];
  }

  interface IpcInvokeChannels {
    get_orders: {
      args: void;
      return: Order[];
    };
    get_order_data: {
      args: string[];
      return: OrderData;
    };
    register_products: {
      args: string;
      return: string;
    };
    extract_invoice: {
      args: string;
      return: string;
    };
    get_email: {
      args: void;
      return: string | undefined;
    };
    save_credentials: {
      empName: string;
      empPass: string;
      cisName: string;
      cisPass: string;
      return: boolean;
    };
  }
}

export {};