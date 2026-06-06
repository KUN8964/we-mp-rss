import { createRouter, createWebHistory } from 'vue-router'
import BasicLayout from '../components/Layout/BasicLayout.vue'
import ExportRecords from '../views/ExportRecords.vue'
import ArticleList from '../views/ArticleList.vue'
import ChangePassword from '../views/ChangePassword.vue'
import EditUser from '../views/EditUser.vue'
import AddSubscription from '../views/AddSubscription.vue'
import WeChatMpManagement from '../views/WeChatMpManagement.vue'
import ConfigList from '../views/ConfigList.vue'
import ConfigDetail from '../views/ConfigDetail.vue'
import MessageTaskList from '../views/MessageTaskList.vue'
import MessageTaskForm from '../views/MessageTaskForm.vue'
import NovelReader from '../views/NovelReader.vue'
import FilterRuleList from '../views/FilterRuleList.vue'
import FilterRuleForm from '../views/FilterRuleForm.vue'
import TaskQueueView from '../views/TaskQueueView.vue'

const routes = [
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: ArticleList,
      },
      {
        path: 'change-password',
        name: 'ChangePassword',
        component: ChangePassword,
      },
      {
        path: 'edit-user',
        name: 'EditUser',
        component: EditUser,
      },
      {
        path: 'add-subscription',
        name: 'AddSubscription',
        component: AddSubscription,
      },
      {
        path: 'wechat/mp',
        name: 'WeChatMpManagement',
        component: WeChatMpManagement,
        meta: { 
          permissions: ['wechat:manage'] 
        }
      },
      
      {
        path: 'configs',
        name: 'ConfigList',
        component: ConfigList,
        meta: { 
          permissions: ['config:view'] 
        }
      },
      {
        path: 'export/records',
        name: 'ExportList',
        component: ExportRecords,
        meta: { 
          permissions: ['config:view'] 
        }
      },
      {
        path: 'configs/:key',
        name: 'ConfigDetail',
        component: ConfigDetail,
        props: true,
        meta: { 
          permissions: ['config:view'] 
        }
      },
      {
        path: 'message-tasks',
        name: 'MessageTaskList',
        component: MessageTaskList,
        meta: { 
          permissions: ['message_task:view'] 
        }
      },
      {
        path: 'message-tasks/add',
        name: 'MessageTaskAdd',
        component: MessageTaskForm,
        meta: { 
          permissions: ['message_task:edit'] 
        }
      },
      {
        path: 'message-tasks/edit/:id',
        name: 'MessageTaskEdit',
        component: MessageTaskForm,
        props: true,
        meta: { 
          permissions: ['message_task:edit'] 
        }
      },
      {
        path: 'sys-info',
        name: 'SysInfo',
        component: () => import('@/views/SysInfo.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'tags',
        name: 'TagList',
        component: () => import('@/views/TagList.vue'),
        meta: { 
          permissions: ['tag:view'] 
        }
      },
      {
        path: 'tags/add',
        name: 'TagAdd',
        component: () => import('@/views/TagForm.vue'),
        meta: { 
          permissions: ['tag:edit'] 
        }
      },
      {
        path: 'tags/edit/:id',
        name: 'TagEdit',
        component: () => import('@/views/TagForm.vue'),
        props: true,
        meta: { 
          permissions: ['tag:edit'] 
        }
      },
      {
        path: 'access-keys',
        name: 'AccessKeyManagement',
        component: () => import('@/views/AccessKeyManagement.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'cascade',
        name: 'CascadeManagement',
        component: () => import('@/views/CascadeManagement.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'cascade/feed-status',
        name: 'CascadeFeedStatus',
        component: () => import('@/views/CascadeFeedStatus.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'env-exception',
        name: 'EnvExceptionStats',
        component: () => import('@/views/EnvExceptionStats.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'filter-rules',
        name: 'FilterRuleList',
        component: FilterRuleList,
        meta: { 
          permissions: ['wechat:manage'] 
        }
      },
      {
        path: 'filter-rules/add',
        name: 'FilterRuleAdd',
        component: FilterRuleForm,
        meta: { 
          permissions: ['wechat:manage'] 
        }
      },
      {
        path: 'filter-rules/edit/:id',
        name: 'FilterRuleEdit',
        component: FilterRuleForm,
        props: true,
        meta: { 
          permissions: ['wechat:manage'] 
        }
      },
      {
        path: 'task-queue',
        name: 'TaskQueue',
        component: TaskQueueView,
        meta: { 
          permissions: ['admin'] 
        }
      },
      {
        path: 'wechat-status',
        name: 'WechatStatus',
        component: () => import('@/views/WechatStatus.vue'),
        meta: { 
          permissions: ['wechat:manage'] 
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/UserManagement.vue'),
        meta: { 
          permissions: ['admin'] 
        }
      },
    ]
  },
  {
    path: '/login',
    redirect: '/'
  },
  {
    path: '/forgot-password',
    redirect: '/'
  },
  {
        path: '/reader',
        name: 'NovelReader',
        component: NovelReader,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 免登录模式：直接放行所有路由
router.beforeEach(async (to, from, next) => {
  next()
})

export default router