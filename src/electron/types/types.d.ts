import { Order} from "./objects.ts";

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

    test: {
      args: void;
      return: string;
    }

    // DATA FROM DB
    get_all_employees_of_team_from_db: {
      args: number;
      return: Employee[];
    },
    get_all_teams_from_db: {
      args: void;
      return: Team[];
    },
    get_all_employees_from_db: {
      args: void;
      return: Employee[];
    },
    get_all_schedule_settings_from_db: {
      args: void;
      return: ScheduleSetting[];
    },

    // DATA TO DB
    update_db_employee: {
      args: Employee;
      return: boolean;
    },
    insert_db_employee: {
      args: Employee;
      return: [boolean, number | bigint];
    },
    delete_db_employee: {
      args: number | bigint;
      return: boolean;
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
