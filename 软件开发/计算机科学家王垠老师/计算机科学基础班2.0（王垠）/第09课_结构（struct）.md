[TOC]

结构类似于 JavaScript 的 object。为了理解结构，我们在解释器和类型检查器里面都加上结构。

- 在解释器里，我们需要加上结构的值。
- 在类型检查器里，我们需要加上结构的类型。

# 结构的值（加入到解释器）

下面是解释器里需要增加的部分，它们用来构造结构（struct），以及结构成员访问（structRef）。
```js
// ---------- struct ----------
// struct 是结构的实现方式。结构其实只是把 table 包装了一下。
// 其中的 members 是一个线性 table，暂不考虑 BST 和其它查找结构。
function struct(members)
{
  return pair("struct", pair(members, null));
}

// 空结构。其它结构均通过调用 addStruct 扩展空结构得到。
// 这很像我们的纯函数 table 的构造方式。
var emptyStruct = struct(emptyTable);

// 结构的类型判断函数
function isStruct(x)
{
  return isPair(x) && first(x) == "struct";
}

// 取得结构里面的数据 table
function structMembers(s)
{
  return first(second(s));
}

// 扩展结构得到一个包含 key，value 的新结构。
// 用 addStruct 函数和 emptyStruct，你可以构造出想要的结构。
function addStruct(key, value, s)
{
  return struct(addTable(key, value, structMembers(s)));
}

// 在结构 s 里面查找成员 key 的值
function lookupStruct(key, s)
{
  return lookupTable(key, structMembers(s));
}

// 把函数 f 作用于结构的每一个成员的值，构造出一个新的结构。
// 为此你需要首先在 table 里面实现一个 mapTable 接口
function mapStruct(f, s)
{
  return struct(mapTable(f, structMembers(s)));
}

// ---------- structRef ----------
// 访问结构的成员 (实现类似 JavaScript 的 s.m 操作)
// 其中：s 是一个任意的表达式，它的值应该是一个结构。
//      m 是一个字符串，表示要访问的成员的名字。
function structRef(s, m)
{
  return pair("structRef", pair(s, pair(m, null)));
}

// structRef 的类型判断函数
function isStructRef(x)
{
  return isPair(x) && first(x) == "structRef";
}

// 访问结构部分（s.m 里的 s）
function structRefStruct(sr)
{
  return first(second(sr));
}

// 访问成员部分（s.m 里的 m）
function structRefMember(sr)
{
  return first(second(second(sr)));
}
```

# expToString 的改动
expToString 需要被扩展，增加显示 struct 和 structRef 的分支。



我们可以用 mapStruct 把结构的值部分都通过 expToString，然后再把整个结构通过 listToString 显示。这个方式可能不符合 JavaScript 的方式，不过我们的目的只是可以看到内容就行。
```js
else if (isStruct(exp))
{
  return listToString(mapStruct(expToString, exp));
}
else if (isStructRef(exp))
{
  return expToString(structRefStruct(exp)) + "." + structRefMember(exp);
}
```
这里是 expToString 需要增加的测试：
```js
test("test expToString struct 1",
     '(struct ((name . "Tom") (color . "grey") (age . 5)))',
     expToString(
       addStruct("name", "Tom",
                 addStruct("color", "grey",
                           addStruct("age", 5,
                                     emptyStruct)))));

test("test expToString struct 2",
     "(struct ((x . 1) (y . (2 * 3))))",
     expToString(
       addStruct("x", 1,
                 addStruct("y", binop("*", 2, 3),
                           emptyStruct))));

test("expToString struct ref",
     "x.a",
     expToString(structRef(variable("x"), "a")));  
```

# 解释器的改动
解释器需要增加 isStruct 和 isStructRef 分支。
```js
else if (isStruct(exp))
{
  // 对结构求值，可以使用 mapStruct
}
else if (isStructRef(exp))
{
  // 对于 s.m，首先求出 s 的值，然后得到它的 m 成员的值
}
```
以下是测试：
```js
// struct
test("test interp struct 1",
     "(struct ((x . 1) (y . 6)))",
     expToString(
       interp(
         addStruct("x", 1,
                   addStruct("y", binop("*", 2, 3),
                             emptyStruct)))));

test("test interp struct 2",
     "(struct ((x . 1) (y . 6)))",
     expToString(
       interp(
         call(
           fun("x",
               addStruct("x", 1,
                         addStruct("y", binop("*", 2, variable("x")),
                                   emptyStruct))),
           3))));

test("struct ref 1",
     1,
     interp(
       structRef(
         addStruct("x", 1,
                   addStruct("y", binop("*", 2, 3),
                             emptyStruct)),
         "x")));

test("struct ref 2",
     6,
     interp(
       structRef(
         addStruct("x", 1,
                   addStruct("y", binop("*", 2, 3),
                             emptyStruct)),
         "y")));

try
{
  interp(
    structRef(
      addStruct("x", 1,
                addStruct("y", binop("*", 2, 3),
                          emptyStruct)),
      "z"));
  console.log("Test struct ref nonexist [FAIL]");
}
catch (e)
{
  test("struct ref not exist",
       "Member does not exist: z",
       e);
}
         
test("struct ref 3",
     6,
     interp(
       call(
         fun("x",
             structRef(
               addStruct("x", 1,
                         addStruct("y", binop("*", 2, variable("x")),
                                   emptyStruct)),
               "y")),
         3)));
```

# 结构的类型（加入到类型检查器）

结构类型（structType）需要添加到类型检查器：
```js
// --------- struct type ----------
// 结构类型构造函数
function structType(members)
{
  return pair("structType", pair(members, null));
}

// 空的结构类型
var emptyStructType = structType(emptyTable);

// 结构类型的类型判断函数
function isStructType(x)
{
  return isPair(x) && first(x) == "structType";
}

// 访问结构类型的内部成员
function structTypeMembers(t)
{
  return first(second(t));
}

// 函数式地扩展结构类型
function addStructType(key, value, s)
{
  return structType(addTable(key, value, structMembers(s)));
}

// 把函数作用于结构类型的每一个成员
function mapStructType(f, s)
{
  return structType(mapTable(f, structTypeMembers(s)));
}

// 判断结构类型的"包含关系"
// 这个关系正好和 subtype 关系相反
function structTypeIncluded(t1, t2)
{
  // TODO
  // 如果 t1 的所有成员都在 t2 里面，而且类型相等，那么就返回 true
  // 提示：为了方便，可以在 table 里面定义一个函数 tableKeys，它会返回给你一个 table 里面所有的 key 在一个链表里面，然后可以在这个链表上使用 map 和 fold。
}
```

# typeToString 的改动

typeToString 函数里应该增加 isStructType 的分支：
```js
else if (isStructType(t))
{
  return listToString(mapStructType(typeToString, t));
}
```

# 类型检查器的改动
subtype 函数里应该增加 isStructType 的分支：
```js
else if (isStructType(t1) && isStructType(t2))
{
  // 结构类型关系正好和 structTypeIncluded 关系相反
  // 结构小的那一边是"父类型"
  return structTypeIncluded(t2, t1);
}
```

在 typecheck 函数里，应该增加 isStruct 和 isStructRef 的分支：
```js
else if (isStruct(exp))
{
  // TODO
}
else if (isStructRef(exp))
{
  // TODO
}
```

以上的改动需要满足以下的基本测试。但请注意，这些测试并不完善，不要依赖于这些测试来写代码，而应该仔细思考。欢迎你指出测试遗漏的地方，或者帮助增加缺少的测试。
```js
var tom = addStruct("name", "Tom",
                    addStruct("color", "grey",
                              addStruct("age", 5,
                                        emptyStruct)));

var Cat = addStructType("name", stringType,
                        addStructType("color", stringType,
                                      addStructType("age", numberType,
                                                    emptyStructType)));

var Animal = addStructType("color", stringType,
                           addStructType("age", numberType,
                                         emptyStructType));


test("typeToString struct",
     "(structType ((name . string) (color . string) (age . number)))",
     typeToString(typecheck(tom)));

test("structTypeIncluded equal",
     true,
     structTypeIncluded(Animal, Cat));

test("structTypeIncluded reversed",
     false,
     structTypeIncluded(Cat, Animal));

test("structTypeIncluded diff key",
     false,
     structTypeIncluded(Animal,
                        addStructType("color", stringType,
                                      addStructType("gender", stringType,
                                                    emptyStructType))));

test("structTypeIncluded diff value",
     false,
     structTypeIncluded(Animal,
                        addStructType("color", numberType,
                                      addStructType("age", numberType,
                                                    emptyStructType))));

test("subtype struct true",
     true,
     subtype(Cat, Animal));

test("subtype struct reverse",
     false,
     subtype(Animal, Cat));

var f1 = funType(Cat, numberType);
var f2 = funType(Animal, numberType);

test("subtype function struct false",
     false,
     subtype(f1, f2));

test("subtype function struct true",
     true,
     subtype(f2, f1));

test("typecheck call with struct",
     "(structType ((x . number) (y . number)))",
     typeToString(
       typecheck(
         call(
           claim(
             funType(numberType,
                     addStructType("x", numberType,
                                   addStructType("y", numberType,
                                                 emptyStructType))),
             fun("x",
                 addStruct("x", 1,
                           addStruct("y", binop("*", 2, variable("x")),
                                     emptyStruct)))),
           5))));

test("typecheck call with struct ref",
     numberType,
     typecheck(
       call(
         claim(
           funType(numberType, numberType),
           fun("x",
               structRef(
                 addStruct("x", 1,
                           addStruct("y", binop("*", 2, variable("x")),
                                     emptyStruct)),
                 "y"))),
         3)));
```




