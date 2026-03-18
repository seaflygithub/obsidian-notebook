[TOC]


这个练习，我们实现一个基础的类型检查器（type checker）。类型检查器的结构很像解释器：

- 解释器输入一个表达式，返回一个值；
- 类型检查器输入一个表达式，返回一个类型。

如果理解了类型就是值的**集合**（set），那你就能理解类型检查器和解释器的相似之处了。如果我们把类型看作一种「抽象的值」（abstract value），那类型检查器就是一种「抽象解释器」（abstract interpreter）。
![[20210411221558074_26461.png]]

类型检查器和解释器的不同之处在于，类型检查器里流动的不是值，而是类型。类型检查器的环境不是从名字到值的映射，而是从名字到类型的映射。另外，类型检查器的函数和调用分支的逻辑和解释器有所不同：类型检查器在函数创建时就处理函数体，而解释器要等到调用的时候才处理函数体（为什么？）



为了简单，这个类型检查器是基于最简单的解释器，只有函数，调用，分支和基本的算术操作，不需要支持 let。


# 类型的数据类型

首先，我们需要定义类型的数据类型，它们是类型检查器内部流动的抽象值。「类型的数据类型」，这个说法似乎有点递归？



像 number, string, boolean 这样的基本类型，它们只有一个名字而没有内部结构。我们可以这样定义**基本类型**（basicType）：
```js
function basicType(name)
{
  return pair("basicType", pair(name, null));
}

function isBasicType(x)
{
  return isPair(x) && first(x) == "basicType";
}

function basicTypeName(bt)
{
  return first(second(bt));
}

// 定义基本类型变量，以后就用这几个变量，而不再重新构造它们。
var numberType = basicType("number");
var stringType = basicType("string");
var booleanType = basicType("boolean");
```

然后，我们需要「**函数类型**」（funType）。比起基本类型，函数类型是有结构的，它的成员是「输入类型」和「输出类型」。函数类型是一个递归数据类型。
```js
function funType(inType, outType)
{
  return pair("funType", pair(inType, pair(outType, null)));
}

function isFunType(x)
{
  return isPair(x) && first(x) == "funType";
}

function funTypeIn(ft)
{
  return first(second(ft));
}

function funTypeOut(ft)
{
  return first(second(second(ft)));
}
```

# 类型标记（claim）

我们需要在原来语言的基础上加上**类型标记**。类型标记是程序员输入的附加信息，用于检查程序没有类型错误。在表达力强的语言里面，类型标记必须是程序员自己写，而没有自动的办法可以生成（推导），因为只有程序员自己才知道代码要做什么。



为了让类型检查器完全独立于解释器，我们不改变解释器的数据类型定义，而是定义一个新的类型标记结构 **claim**。claim 有两个成员，一个是类型（claimType），一个是表达式（claimExp）。它意思是，表达式 claimExp 具有类型 claimType。claimExp 表达式就是原来解释器的表达式，我们只是给它标记了一个类型 claimType。

举一个例子：
```js
claim(
  funType(numberType, numberType),     // number -> number
  fun(variable("x"), variable("x"))    // x => x
)
```

这个 claim 创造了 x => x，并且声明它的类型是 number -> number。这里 number -> number 并不是我们的语言的表达式，而是借用了某些有类型的函数式语言（Haskell）的表达方式，用于简洁地表示函数类型。



在一个具有类型系统的函数式语言里，上面这个 claim 的语法可能是这样：
```js
(x => x) :: (number -> number)
```
其中 :: 表示“左边的表达式具有右边的类型”。



目前，你只需要让 claim 支持函数类型。请拷贝以下的 claim 数据类型：
```js
function claim(claimType, claimExp)
{
  return pair("claim", pair(claimType, pair(claimExp, null)));
}

function isClaim(x)
{
  return isPair(x) && first(x) == "claim";
}

function claimType(c)
{
  return first(second(c));
}

function claimExp(c)
{
  return first(second(second(c)));
}
```

# typeToString
为了直观地显示类型，我们定义一个函数 typeToString，它类似于 pairToString 或 expToString，用于把数据类型转换成字符串。
```js
function typeToString(t)
{
  if (isBasicType(t))
  {
    return basicTypeName(t);
  }
  else if (isFunType(t))
  {
    return "("
           + typeToString(funTypeIn(t))
           + " -> "
           + typeToString(funTypeOut(t))
           + ")";
  }
  else
  {
    throw "Unexpected type: " + t;
  }
}
```

# 子类型关系

类型系统最关键的概念是「子类型关系」（subtype relation）。如果我们把类型看作是值的集合，那么子类型关系其实就是数学里的**子集合**（subset）关系。比如，「猫」是「动物」的子类型，因为猫是动物的子集合。



子类型关系决定了两个类型是否「匹配」。一个例子就是调用函数的时候，输入（argument）的类型必须是参数（parameter）类型的子类型，否则就会出现运行时类型错误。



基本类型的子类型关系就是名字相同。函数的子类型关系课堂上讲过，函数输入的子类型关系是反过来的。在类型理论的文献里，函数的子类型关系规则是这样的：\
![[20210411222041776_29316.png]]

<: 符号表示的就是子类型关系。翻译成自然语言描述就是：如果 C 是 A 的子类型，B 是 D 的子类型，那么 A -> B 就是 C -> D 的子类型。



另外为了方便，我们也定义一个 equalType 函数，它可以用来判断两个类型是相等的。
```js
function subtype(t1, t2)
{
  if (isBasicType(t1) && isBasicType(t2))
  {
    // 基本类型的子类型关系就是类型名字相等
  }
  else if (isFunType(t1) && isFunType(t2))
  {
    // 函数子类型关系请参考上面的公式
    // 注意 <: 是数学公式用的操作符，代码里不能直接写的
    // A <: B 翻译成代码就是 subtype(A, B)
  }
  else
  {
    // 否则就不是子类型
    return false;
  }
}

function equalType(t1, t2)
{
  return subtype(t1, t2) && subtype(t2, t1);
}
```


# 类型检查器

我们可以从解释器的框架出发，把它改造成一个类型检查器。类型检查器为了简单的教学目的，不需要支持 let。



下面是类型检查器的框架代码，请你填入自己的代码。
```js
function typecheck(exp)
{
  function typecheck(exp, env)
  {
    if (typeof (exp) == "number")
    {
      // TODO
    }
    else if (typeof (exp) == "string")
    {
      // TODO
    }
    else if (typeof (exp) == "boolean")
    {
      // TODO
    }
    else if (isVariable(exp))
    {
      // TODO
    }
    else if (isClaim(exp))
    {
      if (isFunType(claimType(exp)))
      {
        if (isFunction(claimExp(exp)))
        {
          // 检查函数表达式 claimExp(exp) 符合声明的类型 claimType(exp)：
          // 1. 把 参数名字 和 声明输入类型 放进扩展的环境
          // 2. 递归求出 函数体 的类型
          // 3. 检查 函数体类型 是 声明输出类型 的子类型
          // 如果符合，就返回 声明函数类型，否则就报错。
          // 返回的应该是 声明函数类型，而不是第2步得到的 函数体类型 (为什么)
          // 报错信息请具体一点，不需要闭包(为什么)
        }
        else
        {
          // 提供合理的报错信息
        }
      }
      else
      {
        // 提供合理的报错信息
      }
    }
    else if (isCall(exp))
    {
      // 递归检查 callOp 的类型，得到 opType。
      // 递归检查 callArg 的类型，得到 argType。
      // 如果 opType 不是函数类型，就报错。
      // 如果 opType 是函数类型，就检查 argType 是 opType 的输入类型的子类型。
      // 如果成功，就返回 opType 的返回类型，否则就报错。
    }
    else if (isIfExp(exp))
    {
      // 条件分支。检查条件的类型，必须是 booleanType。
      // 检查两个分支返回的类型是否相等，
      //   如果不相等就报错，如果相等就返回这个类型。
    }
    else if (isBinOp(exp))
    {
      // 需要支持 +, -, *, /, <, >, ==
      // 输入必须是 number，不支持 string 操作。
      // 根据操作不同，输出可能是 number 或者 boolean。
    }
    else
    {
      throw "illegal expression: " + expToString(exp);
    }
  }

  return typecheck(exp, emptyEnv);
}
```

下面是这个类型检查器需要通过的测试：
```js
// basic types
test("test basic type number",
     "number",
     typeToString(typecheck(2)));

test("test basic type string",
     "string",
     typeToString(typecheck("hi")));

test("test basic type boolean",
     "boolean",
     typeToString(typecheck(true)));

// binop
test("test binop (1 + 2)",
     "number",
     typeToString(typecheck(binop("+", 1, 2))));

test("test binop (1 + (2 * 3))",
     "number",
     typeToString(typecheck(binop("+", 1, binop("*", 2, 3)))));

test("test binop (1 < 2)",
     "boolean",
     typeToString(typecheck(binop("<", 1, 2))));

test("test binop (1 < (2 * 3))",
     "boolean",
     typeToString(typecheck(binop("<", 1, binop("*", 2, 3)))));

try
{
  typecheck(binop("*", 1, "hi"));
  console.log("Test binop input error (1 * 'hi') [FAIL]");
}
catch (e)
{
  test("Test binop input error  (1 * 'hi')",
       "Incorrect input type: number and string",
       e);
}

try
{
  typecheck(binop("<", 1, binop("<", 2, 3)));
  console.log("test binop type error (1 < (2 < 3)) [FAIL]");
}
catch (e)
{
  test("test binop type error (1 < (2 < 3))",
       "Incorrect input type: number and boolean",
       e);
}

// function

test("test function type constant number",
     "(number -> number)",
     typeToString(typecheck(
       claim(
         funType(numberType, numberType),
         fun("x", 42)
       )
     )));

test("test function type constant string",
     "(number -> string)",
     typeToString(typecheck(
       claim(
         funType(numberType, stringType),
         fun("x", "hi")
       )
     )));

test("test function type identity number",
     "(number -> number)",
     typeToString(typecheck(
       claim(
         funType(numberType, numberType),
         fun("x", variable("x"))
       )
     )));

test("test function type identity string",
     "(string -> string)",
     typeToString(typecheck(
       claim(
         funType(stringType, stringType),
         fun("x", variable("x"))
       )
     )));

try
{
  typecheck(
    claim(
      funType(numberType, numberType),
      fun("x", variable("y"))
    )
  );
}
catch (e)
{
  test("Test unbound variable",
       "Unbound variable: y",
       e);
}

try
{
  typecheck(
    claim(
      numberType,
      fun("x", variable("x"))
    )
  );
  console.log("Test type error non-function type [FAIL]");
}
catch (e)
{
  test("Test type error non-function type",
       "Expected function type, but got: number",
       e);
}

try
{
  typecheck(
    claim(
      funType(numberType, stringType),
      fun("x", variable("x"))
    )
  );
  console.log("Test function type error id [FAIL]");
}
catch (e)
{
  test("Test function type error id",
       "Expected output type is string, but got: number",
       e);
}

test("test function type x => (x == 3)",
     "(number -> boolean)",
     typeToString(typecheck(
       claim(
         funType(numberType, booleanType),
         fun("x", binop("==", variable("x"), 3))
       )
     )));


// call

var callId1 = call(
  claim(
    funType(numberType, numberType),
    fun("x", variable("x"))
  ),
  2);

test("test call identity",
     "number",
     typeToString(typecheck(callId1)));

try
{
  typecheck(call(1, 2));
  test("Test callOp type error [FAIL]");
}
catch (e)
{
  test("Test callOp type error",
       "Calling non-function: 1",
       e);
}

var callIdError1 = call(
  claim(
    funType(numberType, numberType),
    fun("x", variable("x"))
  ),
  "hi");

try
{
  typecheck(callIdError1);
  test("Test input type error [FAIL]");
}
catch (e)
{
  test("Test input type error",
       "Incorrect input type. Expected: number, but got: string",
       e);
}


var callBinop1 = call(
  claim(
    funType(numberType, numberType),
    fun("x", binop("+", variable("x"), 3))
  ),
  2);

test("Test call (x => (x + 3)",
     "number",
     typeToString(typecheck(callBinop1)));


var callBinop2 = call(
  claim(
    funType(numberType, booleanType),
    fun("x", binop("<", variable("x"), 3))
  ),
  2);

test("Test call (x => (x < 3)",
     "boolean",
     typeToString(typecheck(callBinop2)));


// curried function
var curriedFun1 =
  claim(
    funType(numberType, funType(numberType, numberType)),
    fun("x",
        claim(
          funType(numberType, numberType),
          fun("y", variable("y")))));

test("test curried function",
     "(number -> (number -> number))",
     typeToString(typecheck(curriedFun1)));

test("test curried function call 1",
     "(number -> number)",
     typeToString(typecheck(call(curriedFun1, 2))));

test("test curried function call 2",
     "number",
     typeToString(typecheck(call(call(curriedFun1, 2), 3))));

// if
var iftype1 = claim(
  funType(numberType, numberType),
  fun("x",
      ifExp(binop("<", variable("x"), 0), 2, 3))
);

test("Test branch type",
     "(number -> number)",
     typeToString(typecheck(iftype1)));


var iftypeError1 = claim(
  funType(numberType, numberType),
  fun("x",
      ifExp(binop("<", variable("x"), 0), "2", 3))
);

try
{
  typecheck(iftypeError1);
  console.log("Test branch type mismatch [FAIL]");
}
catch (e)
{
  test("Test branch type mismatch",
       "Branch types do not match: string and number",
       e);
}

try
{
  typecheck(ifExp(1, 2, 3));
  console.log("Test branch condition type [FAIL]");
}
catch (e)
{
  test("Test branch condition type",
       "Condition must be boolean, but got: number",
       e);
}
```

# 思考题

- 为什么类型检查器在函数的分支处理函数体，而解释器在调用的分支处理函数体？
- Y combinator 的类型是什么？你能否用这个练习里的方式构造写出有类型标记的 Y combinator 而且使它通过类型检查？




