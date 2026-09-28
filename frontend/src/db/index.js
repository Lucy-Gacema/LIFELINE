
import { openDB } from "idb";

const DB_NAME = "lifeline_pos";
const DB_VERSION = 1;

let dbPromise = null;

export function getDb() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains("products")) {
          const store = db.createObjectStore("products", { keyPath: "product_id" });
          store.createIndex("product_name", "product_name");
        }
        if (!db.objectStoreNames.contains("customers")) {
          db.createObjectStore("customers", { keyPath: "customer_id" });
        }
        if (!db.objectStoreNames.contains("sync_queue")) {
          db.createObjectStore("sync_queue", { keyPath: "idempotency_key" });
        }
        if (!db.objectStoreNames.contains("local_sales")) {
          
          db.createObjectStore("local_sales", { keyPath: "idempotency_key" });
        }
        if (!db.objectStoreNames.contains("kv")) {
          db.createObjectStore("kv"); 
        }
      },
    });
  }
  return dbPromise;
}


export async function cacheProducts(products) {
  const db = await getDb();
  const tx = db.transaction("products", "readwrite");
  await Promise.all(products.map((p) => tx.store.put(p)));
  await tx.done;
}

export async function getCachedProducts() {
  const db = await getDb();
  return db.getAll("products");
}


export async function cacheCustomers(customers) {
  const db = await getDb();
  const tx = db.transaction("customers", "readwrite");
  await Promise.all(customers.map((c) => tx.store.put(c)));
  await tx.done;
}

export async function getCachedCustomers() {
  const db = await getDb();
  return db.getAll("customers");
}


export async function queueOperation(operation) {
  const db = await getDb();
  await db.put("sync_queue", operation);
}

export async function getQueuedOperations() {
  const db = await getDb();
  return db.getAll("sync_queue");
}

export async function removeQueuedOperation(idempotencyKey) {
  const db = await getDb();
  await db.delete("sync_queue", idempotencyKey);
}


export async function saveLocalSale(sale) {
  const db = await getDb();
  await db.put("local_sales", sale);
}

export async function getLocalSales() {
  const db = await getDb();
  return db.getAll("local_sales");
}


export async function kvSet(key, value) {
  const db = await getDb();
  await db.put("kv", value, key);
}

export async function kvGet(key) {
  const db = await getDb();
  return db.get("kv", key);
}

export async function kvDelete(key) {
  const db = await getDb();
  await db.delete("kv", key);
}

export function newIdempotencyKey() {
  return crypto.randomUUID();
}
