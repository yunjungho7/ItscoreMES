import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import BaseLayout from '../components/layout/BaseLayout.vue';
import FieldLayout from '../components/layout/FieldLayout.vue';

const routes: RouteRecordRaw[] = [
  // ── 모드 선택 ──
  {
    path: '/select-mode',
    name: 'ModeSelect',
    meta: { title: '모드 선택' },
    component: () => import('../views/ModeSelect.vue'),
  },

  // ── 관리 모드 (기존 BaseLayout) ──
  {
    path: '/management',
    component: BaseLayout,
    children: [
      // ── 대시보드 ──
      {
        path: '',
        name: 'Dashboard',
        meta: { title: '대시보드' },
        component: () => import('../views/management/Dashboard.vue'),
      },

      // ── 1. 물류 ──
      {
        path: 'logistics/sales-order',
        name: 'SalesOrder',
        meta: { title: '수주관리' },
        component: () => import('../views/management/logistics/SalesOrder.vue'),
      },
      {
        path: 'logistics/purchase-order',
        name: 'PurchaseOrder',
        meta: { title: '발주관리' },
        component: () => import('../views/management/logistics/PurchaseOrder.vue'),
      },
      {
        path: 'logistics/purchase-registration',
        name: 'PurchaseRegistration',
        meta: { title: '발주현황/등록' },
        component: () => import('../views/management/logistics/PurchaseRegistration.vue'),
      },
      {
        path: 'logistics/receiving',
        name: 'Receiving',
        meta: { title: '입고관리' },
        component: () => import('../views/management/logistics/Receiving.vue'),
      },
      {
        path: 'logistics/inventory',
        name: 'Inventory',
        meta: { title: '재고관리' },
        component: () => import('../views/management/logistics/Inventory.vue'),
      },
      {
        path: 'logistics/defect',
        name: 'LogisticsDefect',
        meta: { title: '불량관리' },
        component: () => import('../views/management/logistics/Defect.vue'),
      },
      {
        path: 'logistics/shipment',
        name: 'Shipment',
        meta: { title: '출하관리' },
        component: () => import('../views/management/logistics/Shipment.vue'),
      },

      // ── 2. 생산 ──
      {
        path: 'production/plan',
        name: 'ProductionPlan',
        meta: { title: '생산계획' },
        component: () => import('../views/management/production/Plan.vue'),
      },
      {
        path: 'production/work-order',
        name: 'WorkOrder',
        meta: { title: '작업지시' },
        component: () => import('../views/management/production/WorkOrder.vue'),
      },
      {
        path: 'production/status',
        name: 'ProductionStatus',
        meta: { title: '생산현황' },
        component: () => import('../views/management/production/Status.vue'),
      },
      {
        path: 'production/input-material',
        name: 'InputMaterial',
        meta: { title: '투입자재' },
        component: () => import('../views/management/production/InputMaterial.vue'),
      },
      {
        path: 'production/lot',
        name: 'LotManagement',
        meta: { title: 'LOT관리' },
        component: () => import('../views/management/production/Lot.vue'),
      },
      {
        path: 'production/daily-report',
        name: 'DailyReport',
        meta: { title: '작업일보' },
        component: () => import('../views/management/production/DailyInfo.vue'),
      },
      {
        path: 'production/fail-lot',
        name: 'FailLot',
        meta: { title: '불량관리' },
        component: () => import('../views/management/production/FailLot.vue'),
      },

      // ── 3. 검사 ──
      {
        path: 'inspection/items',
        name: 'InspectionItems',
        meta: { title: '검사항목' },
        component: () => import('../views/management/inspection/Items.vue'),
      },
      {
        path: 'inspection/standard',
        name: 'InspectionStandard',
        meta: { title: '기준서관리' },
        component: () => import('../views/management/inspection/Standard.vue'),
      },
      {
        path: 'inspection/report',
        name: 'InspectionReport',
        meta: { title: '검사성적서' },
        component: () => import('../views/management/inspection/Report.vue'),
      },

      // ── 4. 현황 ──
      {
        path: 'status/order',
        name: 'OrderStatus',
        meta: { title: '수주현황' },
        component: () => import('../views/management/status/OrderStatus.vue'),
      },
      {
        path: 'status/purchase',
        name: 'PurchaseStatus',
        meta: { title: '발주현황' },
        component: () => import('../views/management/status/PurchaseStatus.vue'),
      },
      {
        path: 'status/receiving',
        name: 'ReceivingStatus',
        meta: { title: '입고실적' },
        component: () => import('../views/management/status/ReceivingResult.vue'),
      },
      {
        path: 'status/shipment',
        name: 'ShipmentStatus',
        meta: { title: '출하실적' },
        component: () => import('../views/management/status/ShipmentResult.vue'),
      },
      {
        path: 'status/production',
        name: 'ProductionStatusResult',
        meta: { title: '생산현황' },
        component: () => import('../views/management/status/ProductionResult.vue'),
      },
      {
        path: 'status/defect',
        name: 'DefectStatus',
        meta: { title: '불량현황' },
        component: () => import('../views/management/status/DefectStatus.vue'),
      },

      // ── 5. 기준정보 ──
      {
        path: 'master/site',
        name: 'MasterSite',
        meta: { title: '사업장관리' },
        component: () => import('../views/management/master/Site.vue'),
      },
      {
        path: 'master/factory',
        name: 'MasterFactory',
        meta: { title: '공장관리' },
        component: () => import('../views/management/master/Factory.vue'),
      },
      {
        path: 'master/department',
        name: 'MasterDepartment',
        meta: { title: '부서관리' },
        component: () => import('../views/management/master/Department.vue'),
      },
      {
        path: 'master/partner',
        name: 'MasterPartner',
        meta: { title: '거래처관리' },
        component: () => import('../views/management/master/Partner.vue'),
      },
      {
        path: 'master/warehouse',
        name: 'MasterWarehouse',
        meta: { title: '창고관리' },
        component: () => import('../views/management/master/Warehouse.vue'),
      },
      {
        path: 'master/location',
        name: 'MasterLocation',
        meta: { title: 'Location 관리' },
        component: () => import('../views/management/master/Location.vue'),
      },
      {
        path: 'master/line',
        name: 'MasterLine',
        meta: { title: '라인관리' },
        component: () => import('../views/management/master/Line.vue'),
      },
      {
        path: 'master/process',
        name: 'MasterProcess',
        meta: { title: '공정관리' },
        component: () => import('../views/management/master/Process.vue'),
      },
      {
        path: 'master/item',
        name: 'MasterItem',
        meta: { title: '품목관리' },
        component: () => import('../views/management/master/Item.vue'),
      },
      {
        path: 'master/bom',
        name: 'MasterBom',
        meta: { title: 'BOM' },
        component: () => import('../views/management/master/Bom.vue'),
      },
      {
        path: 'master/worker',
        name: 'MasterWorker',
        meta: { title: '공정별작업자' },
        component: () => import('../views/management/master/Worker.vue'),
      },
      {
        path: 'master/common-code',
        name: 'MasterCommonCode',
        meta: { title: '공통코드' },
        component: () => import('../views/management/master/CommonCode.vue'),
      },
      {
        path: 'master/defect-code',
        name: 'MasterDefectCode',
        meta: { title: '불량코드' },
        component: () => import('../views/management/master/DefectCode.vue'),
      },

      // ── 6. 시스템관리 ──
      {
        path: 'system/user',
        name: 'SystemUser',
        meta: { title: '사용자관리' },
        component: () => import('../views/management/system/User.vue'),
      },
      {
        path: 'system/menu',
        name: 'SystemMenu',
        meta: { title: '메뉴관리' },
        component: () => import('../views/management/system/Menu.vue'),
      },
    ],
  },

  // ── 현장 모드 ──
  {
    path: '/field',
    component: FieldLayout,
    children: [
      {
        path: '',
        name: 'FieldProduction',
        meta: { title: '현장생산관리' },
        component: () => import('../views/field/FieldProduction.vue'),
      },
    ],
  },

  // ── 로그인 ──
  {
    path: '/login',
    name: 'Login',
    meta: { title: '로그인' },
    component: () => import('../views/Login.vue'),
  },

  // ── 루트 리다이렉트 ──
  {
    path: '/',
    redirect: '/select-mode',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard
router.beforeEach((to, _from, next) => {
  const user = localStorage.getItem('user');
  
  // If trying to access a protected route without being logged in
  if (to.path !== '/login' && !user) {
    next('/login');
  } 
  // If trying to access login page while already logged in
  else if (to.path === '/login' && user) {
    next('/select-mode');
  } 
  else {
    next();
  }
});

export default router;
