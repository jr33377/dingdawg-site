const https = require('https');

// Credentials from .env file
const CREDENTIALS = {
    SHOPIFY_ACCOUNT_SID: 'IRcZcymc9wen6420145akTB5xMpVxcTCR1',
    SHOPIFY_AUTH_TOKEN: 'J5KWGwX5dDebRJ.egZpKYasL.UMUSCRs'
};

console.log('🔍 Shopify API Connectivity Test');
console.log('=================================');
console.log('Provided Credentials:');
console.log(`SHOPIFY_ACCOUNT_SID: ${CREDENTIALS.SHOPIFY_ACCOUNT_SID}`);
console.log(`SHOPIFY_AUTH_TOKEN: ${CREDENTIALS.SHOPIFY_AUTH_TOKEN}`);
console.log('\n⚠️  WARNING: These credentials do not match standard Shopify API format');
console.log('Standard Shopify API requires:');
console.log('- Shop Domain (e.g., your-shop.myshopify.com)');
console.log('- Access Token (for X-Shopify-Access-Token header)');
console.log('\n');

/**
 * Make a request to Shopify API
 * @param {string} shopDomain - The shop domain (e.g., 'your-shop.myshopify.com')
 * @param {string} endpoint - API endpoint (e.g., '/products.json')
 * @param {string} accessToken - The access token
 */
function makeShopifyRequest(shopDomain, endpoint, accessToken) {
    return new Promise((resolve, reject) => {
        const url = `https://${shopDomain}/admin/api/2024-10${endpoint}`;
        console.log(`📡 Testing URL: ${url}`);
        
        const options = {
            hostname: shopDomain,
            path: `/admin/api/2024-10${endpoint}`,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': accessToken,
                'User-Agent': 'ShopifyAPITest/1.0'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            
            console.log(`📊 Response Status: ${res.statusCode} ${res.statusMessage}`);
            console.log('📋 Response Headers:');
            Object.keys(res.headers).forEach(key => {
                if (key.includes('shopify') || key === 'retry-after' || key === 'content-type') {
                    console.log(`   ${key}: ${res.headers[key]}`);
                }
            });
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        const jsonData = JSON.parse(data);
                        resolve({ success: true, data: jsonData, status: res.statusCode });
                    } else {
                        resolve({ success: false, error: data, status: res.statusCode });
                    }
                } catch (error) {
                    resolve({ success: false, error: data, status: res.statusCode });
                }
            });
        });

        req.on('error', (error) => {
            console.error(`❌ Request Error: ${error.message}`);
            reject(error);
        });

        req.setTimeout(10000, () => {
            console.error('⏰ Request Timeout');
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

/**
 * Test different possible shop domains with the provided credentials
 */
async function testPossibleDomains() {
    const accessToken = CREDENTIALS.SHOPIFY_AUTH_TOKEN;
    
    // Try to extract potential shop name from SHOPIFY_ACCOUNT_SID
    const possibleShopNames = [
        // Direct attempts with the SID
        CREDENTIALS.SHOPIFY_ACCOUNT_SID.toLowerCase(),
        
        // Common shop naming patterns
        'test-shop',
        'demo-shop',
        'my-shop',
        
        // If there are any hints in the SID about the shop name
        'irczcymc9wen6420145aktb5xmpvxctcr1'
    ];

    console.log('🔄 Testing possible shop domains...\n');

    for (const shopName of possibleShopNames) {
        const domain = `${shopName}.myshopify.com`;
        console.log(`\n🧪 Testing domain: ${domain}`);
        console.log('─'.repeat(50));
        
        try {
            // Test shop info endpoint
            console.log('📍 Testing /shop.json endpoint...');
            const shopResult = await makeShopifyRequest(domain, '/shop.json', accessToken);
            
            if (shopResult.success) {
                console.log('✅ SUCCESS! Shop info retrieved:');
                console.log(`   Shop Name: ${shopResult.data.shop.name}`);
                console.log(`   Shop Domain: ${shopResult.data.shop.domain}`);
                console.log(`   Plan: ${shopResult.data.shop.plan_name}`);
                console.log(`   Email: ${shopResult.data.shop.email}`);
                
                // If shop info works, test products
                console.log('\n📦 Testing /products.json endpoint...');
                const productsResult = await makeShopifyRequest(domain, '/products.json?limit=3', accessToken);
                
                if (productsResult.success) {
                    console.log(`✅ Products retrieved! Found ${productsResult.data.products.length} products:`);
                    productsResult.data.products.forEach((product, index) => {
                        const price = product.variants[0]?.price || 'N/A';
                        console.log(`   ${index + 1}. ${product.title} - $${price}`);
                    });
                    
                    // Test product count
                    console.log('\n🔢 Testing /products/count.json endpoint...');
                    const countResult = await makeShopifyRequest(domain, '/products/count.json', accessToken);
                    if (countResult.success) {
                        console.log(`✅ Total products in store: ${countResult.data.count}`);
                    }
                    
                    return { domain, shopResult, productsResult, countResult };
                } else {
                    console.log(`❌ Products fetch failed: ${productsResult.error}`);
                }
            } else {
                console.log(`❌ Shop info failed: ${shopResult.error}`);
            }
            
        } catch (error) {
            console.log(`❌ Connection failed: ${error.message}`);
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return null;
}

/**
 * Test with manual shop domain input
 */
async function testWithManualDomain(shopDomain) {
    const accessToken = CREDENTIALS.SHOPIFY_AUTH_TOKEN;
    const domain = shopDomain.includes('.myshopify.com') ? shopDomain : `${shopDomain}.myshopify.com`;
    
    console.log(`\n🎯 Testing with manual domain: ${domain}`);
    console.log('─'.repeat(50));
    
    try {
        const shopResult = await makeShopifyRequest(domain, '/shop.json', accessToken);
        
        if (shopResult.success) {
            console.log('✅ SUCCESS! Manual domain test passed');
            console.log(`Shop: ${shopResult.data.shop.name}`);
            return shopResult;
        } else {
            console.log(`❌ Manual domain test failed: ${shopResult.error}`);
            return null;
        }
    } catch (error) {
        console.log(`❌ Manual domain test error: ${error.message}`);
        return null;
    }
}

/**
 * Main test function
 */
async function runTests() {
    console.log('🚀 Starting Shopify API Tests...\n');
    
    // Test with possible domains
    const result = await testPossibleDomains();
    
    if (!result) {
        console.log('\n❌ No working shop domain found with automatic detection');
        console.log('\n💡 To test with your actual shop domain, you can:');
        console.log('1. Modify this script to include your shop domain');
        console.log('2. Call testWithManualDomain("your-shop-name") function');
        console.log('3. Verify your access token is correct');
        console.log('\nExample:');
        console.log('testWithManualDomain("my-test-shop").then(result => {');
        console.log('    if (result) console.log("Success!");');
        console.log('});');
    } else {
        console.log('\n🎉 API Test Completed Successfully!');
        console.log(`Working domain: ${result.domain}`);
    }
    
    console.log('\n📚 Next Steps:');
    console.log('1. Verify your shop domain is correct');
    console.log('2. Confirm your access token has the required permissions');
    console.log('3. Check that your app is properly configured in Shopify admin');
    console.log('4. Review the HTML test file for browser-based testing');
}

// Run the tests
runTests().catch(console.error);

// Export functions for manual testing
module.exports = {
    testWithManualDomain,
    makeShopifyRequest,
    CREDENTIALS
};