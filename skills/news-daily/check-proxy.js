#!/usr/bin/env node
/**
 * 代理检测工具
 * 扫描系统上常见的代理客户端
 */

const { execSync } = require('child_process');
const net = require('net');

const PROXY_CLIENTS = [
  { name: 'Clash/ClashX/Clash Verge', port: 7890, type: 'http' },
  { name: 'Clash/ClashX (Mixed)', port: 7897, type: 'http' },
  { name: 'Surge Mac', port: 6152, type: 'http' },
  { name: 'Surge Mac (SOCKS5)', port: 6153, type: 'socks5' },
  { name: 'ShadowsocksX', port: 1080, type: 'socks5' },
  { name: 'ShadowsocksX-NG', port: 1086, type: 'socks5' },
  { name: 'V2Ray', port: 10808, type: 'socks5' },
  { name: 'V2Ray (HTTP)', port: 10809, type: 'http' },
  { name: 'V2RayU', port: 1080, type: 'socks5' },
  { name: 'Quantumult X', port: 8889, type: 'http' },
  { name: 'Quantumult X (SOCKS5)', port: 6170, type: 'socks5' },
  { name: 'Loon', port: 7222, type: 'http' },
  { name: 'Stash', port: 7890, type: 'http' },
  { name: 'Mihomo/Clash.Meta', port: 7890, type: 'http' },
  { name: 'Mihomo (Mixed)', port: 7897, type: 'http' }
];

function checkPort(host, port, timeout = 1000) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(timeout);
    
    socket.on('connect', () => {
      socket.destroy();
      resolve(true);
    });
    
    socket.on('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    
    socket.on('error', () => {
      resolve(false);
    });
    
    socket.connect(port, host);
  });
}

async function testProxy(url, proxyUrl) {
  try {
    const { default: fetch } = await import('node-fetch');
    const { HttpsProxyAgent } = await import('https-proxy-agent');
    
    const agent = new HttpsProxyAgent(proxyUrl);
    const response = await fetch('https://www.google.com/generate_204', {
      agent,
      timeout: 5000
    });
    return response.status === 204;
  } catch {
    return false;
  }
}

async function main() {
  console.log('🔍 正在扫描系统代理...\n');
  
  const found = [];
  
  for (const client of PROXY_CLIENTS) {
    const isOpen = await checkPort('127.0.0.1', client.port);
    if (isOpen) {
      const proxyUrl = `${client.type}://127.0.0.1:${client.port}`;
      process.stdout.write(`  发现 ${client.name} (${proxyUrl}) ... `);
      
      // 测试代理是否可用
      const works = await testProxy('https://www.google.com', proxyUrl);
      if (works) {
        console.log('✅ 可用');
        found.push({ ...client, url: proxyUrl, works: true });
      } else {
        console.log('⚠️ 端口开放但无法连接');
        found.push({ ...client, url: proxyUrl, works: false });
      }
    }
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (found.length === 0) {
    console.log('❌ 未检测到任何代理客户端');
    console.log('\n💡 建议：');
    console.log('  1. 确保代理软件已启动');
    console.log('  2. 检查代理是否允许局域网连接');
    console.log('  3. 手动设置环境变量: export https_proxy=http://127.0.0.1:端口号');
  } else {
    const working = found.filter(f => f.works);
    if (working.length > 0) {
      console.log(`✅ 找到 ${working.length} 个可用代理:\n`);
      working.forEach(p => {
        console.log(`   ${p.name}`);
        console.log(`   地址: ${p.url}`);
        console.log('');
      });
      
      console.log('📝 使用方式:');
      console.log(`   方式1 - 环境变量:`);
      console.log(`     export https_proxy=${working[0].url}`);
      console.log(`   方式2 - 脚本会自动检测，无需配置`);
    } else {
      console.log('⚠️ 发现代理端口但未通过连通性测试');
      console.log('   请检查代理是否正常工作');
    }
  }
}

main().catch(console.error);
