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
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
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

import { getToken } from '@/utils/auth'
import { Message } from '@arco-design/web-vue'

// 路由认证守卫：检查 token 是否存在
// 免登录模式下后端会自动处理无 token 请求，此处仅对敏感路由做前端校验
router.beforeEach(async (to, _from, next) => {
  const token = getToken()
  
  // 登录页和找回密码页始终可访问
  if (to.name === 'Login' || to.name === 'ForgotPassword') {
    next()
    return
  }

  // 若无 token，尝试静默请求后端用户信息来决定是否需要登录
  if (!token) {
    try {
      const { default: http } = await import('@/api/http')
      const res: any = await http.get('/wx/user/info')
      // 后端返回了用户信息，说明免登录模式生效，放行
      if (res?.username) {
        next()
        return
      }
    } catch (_e) {
      // 后端拒绝了未认证请求，需要登录
      // 对于公开页面（首页），仍然放行但后端会自动拒绝未认证 API 调用
    }

    // 需要权限的页面跳转到登录页
    if (to.meta?.permissions) {
      Message.warning('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  next()
})

export default router