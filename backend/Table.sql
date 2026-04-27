CREATE TABLE [dbo].[TBL_PROD_PRODUCEPLAN](
	[PRODUCEDT] [date] NOT NULL,
	[PLANTCD] [varchar](20) NOT NULL,
	[PARTNO] [varchar](50) NOT NULL,
	[ORDERNUM] [varchar](50) NOT NULL,
	[ORDERSEQ] [int] NOT NULL,
	[PRODUCEQTY] [int] NULL,
	[REGUSERID] [int] NOT NULL,
	[REGDTM] [datetime] NOT NULL,
	[EDITUSERID] [int] NULL,
	[EDITDTM] [datetime] NULL,
 CONSTRAINT [PK__TBL_PROD__A056D6025070F446] PRIMARY KEY CLUSTERED 
(
	[PRODUCEDT] ASC,
	[PLANTCD] ASC,
	[PARTNO] ASC,
	[ORDERNUM] ASC,
	[ORDERSEQ] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TBL_PROD_PRODUCEPLAN] ADD  CONSTRAINT [DF_TBL_PROD_PRODUCEPLAN_SEQ]  DEFAULT ((1)) FOR [ORDERSEQ]
GO

ALTER TABLE [dbo].[TBL_PROD_PRODUCEPLAN] ADD  CONSTRAINT [DF__TBL_PROD___PRODU__4E88ABD4]  DEFAULT ((0)) FOR [PRODUCEQTY]
GO


CREATE TABLE [dbo].[TBL_PROD_WORKORDER](
	[WORKORDNO] [varchar](20) NOT NULL,
	[PAR_WORKORDNO] [varchar](20) NULL,
	[PLANTCD] [varchar](20) NULL,
	[PROCESSCD] [varchar](20) NULL,
	[SHIFT] [varchar](20) NULL,
	[EQUIPCD] [varchar](20) NULL,
	[PARTNO] [varchar](50) NULL,
	[ORDQTY] [decimal](18, 4) NULL,
	[ORDTYPE] [varchar](20) NULL,
	[ORDpriority] [int] NULL,
	[ORDDATE] [varchar](10) NULL,
	[STDATE] [varchar](10) NULL,
	[STTIME] [varchar](5) NULL,
	[ENDDATE] [varchar](10) NULL,
	[ENDTIME] [varchar](5) NULL,
	[CLOSEYN] [bit] NULL,
	[CLOSEDATE] [varchar](10) NULL,
	[CLOSETIME] [varchar](5) NULL,
	[FIXEDYN] [bit] NULL,
	[FIXEDTM] [datetime] NULL,
	[HOLDYN] [bit] NULL,
	[ORDSTATE] [varchar](20) NULL,
	[LINECD] [varchar](20) NULL,
	[USEYN] [bit] NOT NULL,
	[REGUSERID] [int] NOT NULL,
	[REGDTM] [datetime] NOT NULL,
	[EDITUSERID] [int] NOT NULL,
	[EDITDTM] [datetime] NOT NULL,
	[REWORKYN] [varchar](20) NULL,
	[REWORKLOTNO] [varchar](30) NULL,
	[FAILTYPE] [varchar](30) NULL,
	[FAILBREAKDOWN] [varchar](30) NULL,
	[ALARM1] [varchar](2) NULL,
	[ALARM2] [varchar](2) NULL,
	[REMARK] [nvarchar](2000) NULL,
 CONSTRAINT [PK_TBL_PROD_WORKORD] PRIMARY KEY CLUSTERED 
(
	[WORKORDNO] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TBL_PROD_WORKORDER] ADD  CONSTRAINT [DF_TBL_PROD_WORKORDER_USEYN]  DEFAULT ((1)) FOR [USEYN]
GO

ALTER TABLE [dbo].[TBL_PROD_WORKORDER]  WITH CHECK ADD  CONSTRAINT [FK_PROD_WORKORD] FOREIGN KEY([PAR_WORKORDNO])
REFERENCES [dbo].[TBL_PROD_WORKORDER] ([WORKORDNO])
GO

ALTER TABLE [dbo].[TBL_PROD_WORKORDER] CHECK CONSTRAINT [FK_PROD_WORKORD]
GO

ALTER TABLE [dbo].[TBL_PROD_WORKORDER]  WITH NOCHECK ADD  CONSTRAINT [FK_PROD_WORKORD_PARTNO] FOREIGN KEY([PARTNO])
REFERENCES [dbo].[TBL_COM_GOODS] ([PARTNO])
GO

ALTER TABLE [dbo].[TBL_PROD_WORKORDER] CHECK CONSTRAINT [FK_PROD_WORKORD_PARTNO]
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'작업지시번호' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'WORKORDNO'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'상위작업지시번호' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'PAR_WORKORDNO'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'사업장코드' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'PLANTCD'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'공정코드' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'PROCESSCD'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'근무조코드(SHIFTGUBUN000)' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'SHIFT'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'설비코드' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'EQUIPCD'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'품번코드' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'PARTNO'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'지시수량' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ORDQTY'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'작업지시구분(ORDGUBUN000)' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ORDTYPE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'우선순위' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ORDpriority'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'작업지시일자' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ORDDATE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'시작일자' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'STDATE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'시작일시' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'STTIME'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'완료일자' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ENDDATE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'완료시간' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ENDTIME'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'마감여부' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'CLOSEYN'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'마감일자' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'CLOSEDATE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'마감시간' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'CLOSETIME'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'확정여부' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'FIXEDYN'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'확정일시' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'FIXEDTM'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'홀드여부' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'HOLDYN'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'작지상태(ORDSTATE000)' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'ORDSTATE'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'등록자사번' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'REGUSERID'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'등록일시' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'REGDTM'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'변경자사번' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'EDITUSERID'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'변경일시' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'TBL_PROD_WORKORDER', @level2type=N'COLUMN',@level2name=N'EDITDTM'
GO



-- ==============================================
-- 시스템관리 - 사용자관리 (TBL_COM_MEMBERS)
-- ==============================================
CREATE TABLE [dbo].[TBL_COM_MEMBERS](
	[ID] [int] IDENTITY(115,1) NOT NULL,
	[PLANT] [varchar](50) NOT NULL,
	[GUBUN] [char](1) NOT NULL,
	[EMPID] [varchar](20) NOT NULL,
	[NAME] [nvarchar](20) NOT NULL,
	[EMAIL] [nvarchar](100) NULL,
	[DEPTCD] [nvarchar](20) NULL,
	[JIKGUB] [nvarchar](20) NULL,
	[PASS] [nvarchar](50) NULL,
	[SECURE_GRADE] [nvarchar](3) NULL,
	[USEAREA] [nvarchar](100) NULL,
	[PARTNERSHOWYN] [char](1) NULL,
	[TEL] [nvarchar](20) NULL,
	[MOBILE] [nvarchar](20) NULL,
	[PASSYN] [char](1) NULL,
	[PASSWRITERID] [nvarchar](20) NULL,
	[SHOWYN] [bit] NULL,
	[PASSDATE] [datetime] NULL,
	[WDATE] [datetime] NOT NULL,
	[LOGINYN] [char](1) NULL,
	[LOGINDATE] [datetime] NULL,
	[LOGOUTDATE] [datetime] NULL,
	[SESSIONTIME] [int] NOT NULL,
	[OUTERACCESSYN] [char](1) NOT NULL,
	[CHIEFYN] [varchar](1) NULL,
	[PASSWD] [nvarchar](50) NULL,
	[PLANTAREA] [nvarchar](100) NULL,
	[FROMTODAY] [tinyint] NULL,
	[PARTNERGUBUN] [nvarchar](20) NULL,
	[MANAGERYN] [char](1) NULL,
 CONSTRAINT [PK_TBL_COM_MEMBERS] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TBL_COM_MEMBERS] ADD  CONSTRAINT [DF_TBL_COM_MEMBERS_WDATE]  DEFAULT (getdate()) FOR [WDATE]
GO
ALTER TABLE [dbo].[TBL_COM_MEMBERS] ADD  CONSTRAINT [DF_TBL_COM_MEMBERS_SESSIONTIME]  DEFAULT ((1440)) FOR [SESSIONTIME]
GO
ALTER TABLE [dbo].[TBL_COM_MEMBERS] ADD  CONSTRAINT [DF_TBL_COM_MEMBERS_OUTERACCESSYN]  DEFAULT ((1)) FOR [OUTERACCESSYN]
GO

-- ==============================================
-- 시스템관리 - 메뉴관리 (TBL_COM_MENU)
-- ==============================================
CREATE TABLE [dbo].[TBL_COM_MENU](
	[MENUCD] [varchar](20) NOT NULL,
	[PAR_MENUCD] [varchar](20) NULL,
	[MENUNM] [nvarchar](50) NULL,
	[CLASS_PATH] [nvarchar](500) NULL,
	[ORD] [tinyint] NULL,
	[SEARCH] [bit] NULL,
	[REGEDIT] [bit] NULL,
	[REGUSERID] [int] NULL,
	[REGDTM] [datetime] NULL,
	[EDITUSERID] [int] NULL,
	[EDITDTM] [datetime] NULL,
	[USE_YN] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[MENUCD] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[TBL_COM_MENU] ADD  DEFAULT ((0)) FOR [ORD]
GO
ALTER TABLE [dbo].[TBL_COM_MENU] ADD  DEFAULT ((1)) FOR [USE_YN]
GO
EXEC sys.sp_addextendedproperty @name=N''MS_Description'', @value=N''조회'' , @level0type=N''SCHEMA'',@level0name=N''dbo'', @level1type=N''TABLE'',@level1name=N''TBL_COM_MENU'', @level2type=N''COLUMN'',@level2name=N''SEARCH''
GO
EXEC sys.sp_addextendedproperty @name=N''MS_Description'', @value=N''등록/수정'' , @level0type=N''SCHEMA'',@level0name=N''dbo'', @level1type=N''TABLE'',@level1name=N''TBL_COM_MENU'', @level2type=N''COLUMN'',@level2name=N''REGEDIT''
GO
