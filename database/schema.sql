-- Database Schema for SpiderMail Project
-- PostgreSQL database schema for storing e-commerce product and review data

-- 商品信息表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) UNIQUE NOT NULL,  -- 商品唯一标识
    platform VARCHAR(20) NOT NULL,            -- 平台名称 (taobao/jd)
    title TEXT NOT NULL,                      -- 商品标题
    brand VARCHAR(100),                       -- 品牌
    price DECIMAL(10,2),                      -- 价格
    original_price DECIMAL(10,2),             -- 原价
    discount_rate DECIMAL(5,2),               -- 折扣率
    sales_count INTEGER DEFAULT 0,           -- 销量
    review_count INTEGER DEFAULT 0,          -- 评论数量
    rating DECIMAL(3,2),                     -- 平均评分
    category VARCHAR(100),                   -- 分类
    subcategory VARCHAR(100),                -- 子分类
    image_urls TEXT[],                       -- 商品图片URLs
    description TEXT,                        -- 商品描述
    specifications JSONB,                    -- 商品规格 (JSON格式)
    shop_name VARCHAR(200),                  -- 店铺名称
    shop_url VARCHAR(500),                   -- 店铺链接
    location VARCHAR(100),                   -- 发货地
    shipping_info TEXT,                      -- 物流信息
    tags TEXT[],                             -- 商品标签
    status VARCHAR(20) DEFAULT 'active',     -- 商品状态
    source_url VARCHAR(1000),                -- 源链接
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评论信息表
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    review_id VARCHAR(100) UNIQUE NOT NULL,   -- 评论唯一标识
    product_id VARCHAR(100) NOT NULL,         -- 关联商品ID
    platform VARCHAR(20) NOT NULL,           -- 平台名称
    user_name VARCHAR(100),                   -- 用户名 (脱敏处理)
    user_level VARCHAR(50),                   -- 用户等级
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),  -- 评分 1-5星
    content TEXT,                             -- 评论内容
    pros TEXT,                                -- 优点
    cons TEXT,                                -- 缺点
    images TEXT[],                           -- 评论图片URLs
    helpful_count INTEGER DEFAULT 0,         -- 有用数
    reply_count INTEGER DEFAULT 0,           -- 回复数
    purchase_time DATE,                      -- 购买时间
    review_time TIMESTAMP NOT NULL,          -- 评论时间
    specifications JSONB,                    -- 购买时的规格信息
    verified_purchase BOOLEAN DEFAULT FALSE, -- 是否验证购买
    is_top_review BOOLEAN DEFAULT FALSE,     -- 是否优质评论
    sentiment_score DECIMAL(3,2),            -- 情感分析得分
    keywords TEXT[],                         -- 关键词
    source_url VARCHAR(1000),               -- 源链接
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 价格历史表
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    discount_rate DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 爬虫任务记录表
CREATE TABLE crawl_tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'running',  -- running, completed, failed
    products_found INTEGER DEFAULT 0,
    reviews_found INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_messages TEXT[],
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引提高查询性能
CREATE INDEX idx_products_platform ON products(platform);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_platform ON reviews(platform);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_review_time ON reviews(review_time);
CREATE INDEX idx_price_history_product_id ON price_history(product_id);
CREATE INDEX idx_crawl_tasks_platform ON crawl_tasks(platform);
CREATE INDEX idx_crawl_tasks_status ON crawl_tasks(status);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();