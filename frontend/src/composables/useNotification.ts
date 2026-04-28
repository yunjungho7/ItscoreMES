import { reactive } from 'vue';

export interface Notification {
  id: number;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  statusCode?: number;
  duration?: number;
}

const state = reactive<{ notifications: Notification[] }>({
  notifications: [],
});

let nextId = 0;

export function useNotification() {
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = nextId++;
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000,
    };
    state.notifications.push(newNotification);

    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }
  };

  const removeNotification = (id: number) => {
    const index = state.notifications.findIndex((n) => n.id === id);
    if (index !== -1) {
      state.notifications.splice(index, 1);
    }
  };

  return {
    notifications: state.notifications,
    addNotification,
    removeNotification,
    notifyError: (message: string, statusCode?: number) =>
      addNotification({ message, type: 'error', statusCode }),
    notifySuccess: (message: string) =>
      addNotification({ message, type: 'success' }),
    notifyWarning: (message: string) =>
      addNotification({ message, type: 'warning' }),
    notifyInfo: (message: string) =>
      addNotification({ message, type: 'info' }),
  };
}
