[TOC]



# 课堂笔记

表达式和值的理解：
![[20210411165507013_8036.png]]

计算的过程就是求值的过程。

```js
2 > 3 //output: false
2 < 3 //output: true
2 == 3 //output: false
2 != 3 //output: true

2 >= 3 //output: false
2 >= 2 //output: true
```

布尔类型: boolean

什么是类型？\
之前有==数字==，现在有==boolean==，......\
我们可以把上面的数字和boolean看成两个集合，\
number{2,1,3,0,...}\
boolean{true, false}

字符串型:string，例如 "hello"
```js
"hello" < "hel" //false
"hello" < "hallo" //false
"hello" < "hi" //true
//按照字典里单词的顺序来比较
```

讲布尔类型，目的是为了增加一个概念。

这个新的概念，叫做==条件分支==，

什么是条件分支？
```js
if (可以返回布尔类型的表达式)
{
    console.log("yes");
} else 
{
    console.log("no");
}
```

```js
function f(x)
{
    return x < 5;
}
f(2) //true
f(6) //false
```

```js
function abs(x)
{
    if (x < 0)
    {
        return -x;
    }
    else
    {
        return x;
    }
}
abs(-2);//2
abs(-3.5);//3.5
```

符号函数:如果你给它负数,他就给你返回-1;如果给它正数,它就给你返回1;如果给它0，他就返回0.
```js
function sign(x)
{
    if (x < 0)
    {
        return -1;
    }
    else
    {
        if (x == 0)
        {
            return 0;
        }
        else
        {
            return 1;
        }
    }
}

function sign(x)
{
    if (x < 0)
    {
        return -1;
    }
    else if (x == 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

```

阶加：**sum**, 5+4+3+2+1+0，n + (n-1) + ... + 0
```js
function sum(n)
{
    if (n > 0)
    {
        return n + sum(n - 1);
    }
    else //n <= 0
    {
        return 0;
    }
}
show(sum(5));//5+4+3+2+1+0
```


阶乘：factorial
```js
    //数学表达阶乘: 
    //5! = 5 * 4 * 3 * 2 * 1
    //4! = 4 * 3 * 2 * 1
    
    //5! = 5 * 4!
    //4! = 4 * 3!
    //......
    //n! = n * (n - 1)! //所有自然数的阶乘
    
function fact(n)
{
    if (n > 0)
    {
        return n * fact(n - 1);
    }
    else //n <= 0
    {
        return 1;
    }
}
fact(0);//1
fact(1);//1
fact(2);//2
fact(3);//6
fact(4);//24
fact(5);//120

```


调用一个正在定义的函数，是不是有矛盾？

怎么做到n只取自然数呢？\
一般我们都会对参数进行检查。
fact递归从终止条件处_反方向算回去:
![[20210411165601665_28832.png]]

这个3， 2， 1需要存下来不是很理解。

需要存储很多中间结果

求斐波拉契数序列：
```js
function fib(n)
{
    //f(0) = 0;
    //f(1) = 1;
    //F(2) = F(1);
    //F(3) = F(2) + F(1);
    //F(4) = F(3) + F(2) + F(1)
    //F(n) = F(n-1) + F(n-2) + ...
    if (n > 1)
    {
        return fib(n - 1) + fib(n - 2);
    }
    else if (n == 0)
    {
        return 0;
    }
    else if (n == 1)
    {
        return 1;
    }
}
fib(8);//21
fib(7);//13
```
斐波拉契数序:
![[20210411165719102_24944.png]]

递归结构标注:
![[20210411165747772_2279.png]]

递归结构标注2:
![[20210411165815872_28287.png]]

递归fib计算效率次数统计:
![[20210411165842382_3249.png]]

递归fib计算效率次数统计2:\
![[20210411165917024_23638.png]]

递归调用：recursive call\
递归：recursion\
递归分支/递归情况：recursive case

很慢，我刚尝试 fib(90) 现在还没结束

fib有快一点的写法，但是我们这节课暂时不考虑，因为我们这节课重点是递归。

这种重复计算很慢的递归叫==树递归==。

如果这样算很慢的话，为什么这个数列是这个公式而不是更快的公式呢？

这个公式并不慢，慢的是用递归来实现它

前面的fact是树递归吗？线性递归

如果有3个调用，是不是有3叉？\
答：应该是的吧。

编程越省资源越好吗？ 是不是有节省资源的做法。\
答：这个要折中考虑，在资源充足情况下，就像省钱一样，要把大头省下来；最重要是保证做对。\
C语言程序员对细枝末节都很在意，导致他们的代码最终别人不容易看懂；感觉多一次函数调用他们都很心疼。

如果一个数字1，我把它当做布尔类型，会怎么样呢？\
答：还记得刚刚那两个集合吗，布尔类型只有true,false；虽然很多编程语言支持把数字当成布尔类型，但它们这是错误的做法。

编程的时候是不是要尽量避免递归，因为递归效率不是很高\
答：这里的演示函数只是为了讲解递归，并不等于你不能写出效率高的递归来。

比如数据结构中的树：\
有些人表面上可以消除递归，树这种数据结构必须用递归，他们所说的消除，其实是中间过程被他们自己管理起来了，本质上他们还是没摆脱递归。

递归是不是来自于数学里的“数学归纳法”？

在设计和递归相关的程序的时候，是不是应该事先对整个计算流图有个清晰的认识呢？感觉有些递归相关的程序题目挺难想清楚的，有没有一些方法来帮助思考呢？\
答：

单步替换的顺序是从外到内吗？对它的顺序有些含糊\
答：这其实是一个参数，不是两个参数\
![[20210411165950235_26916.png]]



# 作业提交与反馈(微信多对一辅导群)

**【SeaflyWechat】**


## show
下面先把课堂上讲过的两个函数自己写一遍，然后做更近一步的练习。

这次练习因为可能在 Webstorm 这类专业环境运行，所以你需要用一个"显示函数"才能显示出结果。JavaScript 的 console.log 函数可以显示出值来，但它名字太长。你可以定义一个函数名叫 show 来方便使用 console.log：
```js
var show = console.log;
```
下面练习的测试都会有 show(...) 这个函数包在结果外面，就是调用这个函数。

**注意**：不要在练习的函数里使用 show。show 只是在测试的时候显示结果用的。练习的函数还是应该照常返回一个值，而不应该直接显示结果。想想为什么？

我的理解：show是打印函数，即函数；在递归调用这类函数会严重影响效率和性能。



## abs
写一个函数 abs，输入一个数 n，它给你 n 的「绝对值」。

举例：
```js
abs(1) = 1
abs(-5) = 5
abs(9) = 9
abs(0) = 0
abs(-42.8) = 42.8
```


**【SeaflyWechat】**
```js
var show = console.log;

function abs(x)
{
    if (x < 0)
    {
        return -x;
    }
    else
    {
        return x;
    }
}
show(abs(-5));
```


## sign

写一个函数 sign，输入一个数 n，它给你这个数的「符号」，用 -1, 0, 或者 1 表示。对正数返回 1，对负数返回 -1，对 0 返回 0。

举例：
```js
sign(4) = 1
sign(-17) = -1
sign(0) = 0
sign(4.2) = 1
sign(-34.3) = -1
```

**【SeaflyWechat】**
```js
function sign(n)
{
    if (n < 0)
    {
        return -1;
    }
    else if (n == 0)
    {
        return 0;
    }
    else 
    {
        return 1;
    }
}
show(sign(-42.8));
```

## sum
写一个函数 sum，输入一个自然数 n（从 0 开始的整数），它给你从 0 “连加”到 n 的和，也就是 0 + 1 + 2 + ... + n。不用考虑输入不符合“自然数”条件的情况。
```js
function sum(n)
{
  //____
}

show(sum(5));    // 15
```
**提示**：sum 很像 fact（为什么），所以它的结构类似于 fact。


**【SeaflyWechat】**
```js
function sum(n)
{
    if (n == 0)
    {
        return 0;
    }
    else
    {
        return n + sum(n - 1);
    }
}
```

## accum
观察一下 sum 和 fact，它们有什么相似和不同点？

提取出它们的共同点作为「框架」，把它们的不同点作为「参数」，你可以写出一个函数 accum。accum 接受 3 个参数。unit 是 base case 返回的值（0 或者 1），combine 是递归情况返回时进行的“组合操作”（比如 + 或者 *）。

之后，我们就能用 accum 来重新定义 sum 和 fact。
```js
function accum(n, unit, combine)
{
    // ____
}

function sum2(n)
{
    return accum(n, 0, (x, y) => x + y);
}

show(sum2(0)); // 0
show(sum2(1)); // 1
show(sum2(5)); // 15

function fact2(n)
{
    return accum(n, 1, (x, y) => x * y); 
}

show(fact2(0)); // 1
show(fact2(1)); // 1
show(fact2(5)); // 120
```
你会发现 accum 是一个更加“通用”的函数。这种接受函数作为输入，实现通用功能的函数，叫做“**高阶函数**”(high-order function)。



**【SeaflyWechat】**
```js
function accum(n, unit, combine)
{
    if (n == unit)
    {
        return unit;
    }
    else
    {
        return combine(n, accum(n - 1, unit, combine));
    }
}

function sum2(n)
{
    return accum(n, 0, (x, y) => x + y);
}

function fact2(n)
{
    return accum(n, 1, (x, y) => x * y); 
}

show(sum2(0));//0
show(sum2(5));//15
show(fact2(0));//1
show(fact2(5));//120
```


**【计算机科学家王垠老师ian】**\
看看 fact2(0)对不对？


**【SeaflyWechat】**\
好的，确实有问题，我修改一下：
```js
function accum(n, unit, combine)
{
    if ((n == unit) || (n < unit))
    {
        return unit;
    }
    else
    {
        return combine(n, accum(n - 1, unit, combine));
    }
}

function sum2(n)
{
    return accum(n, 0, (x, y) => x + y);
}

function fact2(n)
{
    return accum(n, 1, (x, y) => x * y); 
}

show(sum2(0));//0
show(sum2(5));//15
show(fact2(0));//1
show(fact2(5));//120
```

**【计算机科学家王垠老师ian】**\
不对，你要理解 unit 是 base case 返回的值，而不是 base case 的条件。

**【SeaflyWechat】**\
哦，好，我先理解一下您这句话

**【计算机科学家王垠老师ian】**\
你看一下 sum 和 fact，仔细对比一下是哪里不同，那些地方是一样的。

**【SeaflyWechat】**\
好的，我看看

**【SeaflyWechat】**\
sum 和 fact相同点：\
1、都是从n开始，数字n逐渐递减\
2、分支条件都相同，分支数也相同\
3、当n<=0时，就进入base case。

**【SeaflyWechat】**\
sum 和 fact不同点：\
1、base case处返回值不同。\
2、运算操作符不同，sum是+，fact操作符是*。


## sumFrom
写一个函数 sumFrom，输入自然数 a 和 b，它从 a 连加到 b，也就是 a + ... + b。你可以假定输入满足 a <= b。

**注意**：sumFrom 不要调用 sum，请直接写一个递归函数。
```js
function sumFrom(a, b)
{
  //____
}

show(sumFrom(3, 3));    // 3
show(sumFrom(3, 5));    // 12
```



**【SeaflyWechat】**
```js
function sumFrom(a, b)
{
    //a+0, a+1, a+2, a+3, ...b
    if (a < b)
    {
        return a + sumFrom(a + 1, b);
    }
    else if (a == b)
    {
        return a;
    }
    else //a > b
    {
        return -1;
    }
}
show(sumFrom(3, 5));// 12
```

## expt

写一个函数 expt，输入自然数 b (base) 和 e (exponent)，它计算 b 的 e 次方的值。注意不要只是调用系统函数，应该自己用乘法来实现。

**注意**：输入 e 可以是 0。
```js
function expt(b, e)
{
  //____
}

show(expt(2, 0));    // 1
show(expt(3, 4));    // 81
```


**【SeaflyWechat】**
```js
function expt(b, e)
{
    // 2^0 == 1
    // 3^4 == 3 * 3 * 3 * 3;
    if (e == 0)
    {
        return 1;
    }
    else //e > 0
    {
        return b * expt(b, e - 1);
    }
}

show(expt(2, 0));    // 1
show(expt(3, 4));    // 81
```

**【计算机科学家王垠老师ian】**\
你的base case很多是用大于小于号区分的，这样表达不清晰。base case应该很明显的知道到底什么时候停下来。如果等于某个数，最好是用等号。

**【SeaflyWechat】**\
哦，好的老师

**【SeaflyWechat】**\
我这个位置可能是受到您网上文章的影响而这样写的，当时是直接把您文章描述的意图挪用过来的，“我这里没有使用意图清晰的base case，就是考虑到调用者大部分是很少传入其他特殊值，就可以不必进入下一个判断分支，从而节省分支判断时间”。。。

**【SeaflyWechat】**\
方法我用的比较死板，就是套用，这个还需要深刻理解，还需要在实际练习中摆脱这种死板的套用。

## nest

写一个函数 nest，输入函数 f 和自然数 n，它返回一个新的函数。这个函数类似之前做过的 two，只是它会把 f 嵌套作用于它的参数 n 次，而不只是 2 次。nest(f, n) 应该相当于 x => f(f(f ... f(x)))。中间有 n 个 f 嵌套在一起。

**注意**：输入 n 可以是 0。
```js
function nest(f, n)
{
  //____
}

show(nest(x => x + 1, 0)(3));  // 3
show(nest(x => x + 1, 7)(0));  // 7
show(nest(x => x * x, 3)(2));  // 256
 
show(nest(x => 1 + 1/x, 100)(3));    // 这个结果看起来像什么数？
show(nest(x => 1 + 1/x, 100)(42));
show(nest(x => 1 + 1/x, 100)(-42));
```



**【SeaflyWechat】**\
第nest题提交如下：
```js
function nest(f, n)
{
    
    if (n == 0)
    {
        return x => x;
    }
    else
    {
        return x => f(nest(f, n - 1)(x));
    }
}
show(nest(x => x + 1, 0)(3)); // 3
show(nest(x => x + 1, 7)(0)); // 7
show(nest(x => x * x, 3)(2)); // 256

show(nest(x => 1 + 1/x, 100)(3)); // 这个结果看起来像什么数？1.618033988749895
show(nest(x => 1 + 1/x, 100)(42)); // 这个结果看起来像什么数？1.618033988749895
show(nest(x => 1 + 1/x, 100)(-42)); // 这个结果看起来像什么数？1.618033988749895
```

f(...(f(f(f(f(f(f(x)))))))\
1 + 1/3 == 1.3333333333333...\
1 + 1/(1 + 1/3) == 1.75\
1 + 1/1.75 == 1.5714285714285714285714285714286\
1 + 1/(1 + 1/1.75) == 1.6363636363636363636363636363636\
1 + 1/(1 + 1/(1 + 1/1.75)) == 1.6111111111111111111111111111111\
1 + 1/(1 + 1/(1 + 1/(1 + 1/1.75))) == 1.6206896551724137931034482758621\
1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/1.75)))) == 1.6170212765957446808510638297872\
1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/1.75))))) == 1.6184210526315789473684210526316\
1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/1.75)))))) == 1.6178861788617886178861788617886\
1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/(1 + 1/1.75))))))) == 1.6180904522613065326633165829146
...


## fix
Write a function fix(), There are three parameters：A function f ，An initial value Start，A tolerance value tolerance. fix() returns a number. FIX is a bit similar to Nest, But it will f nested role uncertain how many times in its arguments，直到结果的变化的绝对值小于 tolerance。你可以认为这个 tolerance 是结果的精度。

形象地说，就是计算 f(f(f...f(start)...))，嵌套的 f 的数目正好可以让结果趋于稳定。增加一层嵌套，变化不超过 tolerance。这个结果通常叫做函数 f 的**不动点**（fixed point）。
```js
function fix(f, start, tolerance)
{
  // 从 start 开始，把 f 反复嵌套于一个起始值
  // 直到结果的变化的绝对值小于 tolerance
}
 
show(fix(x => 1 + 1/x, 42, 0.01));
// 1.6155234657039712
 
show(fix(x => 1 + 1/x, -17, 0.0000000000000001));
// 1.618033988749895
```
**注意**：函数的计算不应该出现重复计算。如果有，请使用变量来消除重复计算。

**提示 1**：fix 的结构跟 nest 不一样，所以不要模仿 nest 的构造，也不要在 fix 里面调用 nest。另外写一个新的递归函数就行了。


## 限制 fix 的递归深度

如果 fix 的输入函数不是一个具有不动点的函数，比如 x => x * 2 这样会不断增加的，那么 fix 就会"发散"（diverge），也就是说进入"死循环"出不来了。

所以在安全性要求较高的应用中，这类函数往往会被加上一个上限。如果超过了某个递归深度还没有达到结果，就停下来报告失败，而不是一直进行下去。

现在请你给 fix 的末尾加上一个参数，叫 depth。
```js
function fix(f, start, tolerance, depth)
{
  // ...
}

show(fix(x => 1 + 1/x, -17, 0.0000000000000001, 100));
// 1.618033988749895

show(fix(x => 1 + 1/x, -17, 0.0000000000000001, 10));
// 报错 "over depth limit"

show(fix(x => x * 2, 56, 0.0000000000000001, 1000));
// 报错 "over depth limit"
```

如果递归深度超过了 depth 就停下来，报告错误"over depth limit"。报告错误的方式可以使用 JavaScript 的报错语句 **throw**，比如：```throw "over depth limit";```
这种 throw 语句类似于 return，只不过它会终止程序的运行，并且显示指定的信息，而不是正常的返回一个值。throw 可以出现在 return 会出现的那种"返回位置"。有了 throw 就不要再在同样位置写 return 了。

**提示**：可以使用之前定义的 abs 函数来计算绝对值。

## checkStrange
有一个叫 strange 的函数，参数 n 是一个**正整数**。strange 的定义是这样：
```js
function strange(n)
{
  if (n % 2 == 0)    // 如果 n 是偶数
  {
    return n / 2;
  }
  else
  {
    return 3 * n + 1;
  }
}
```

strange 的意思，用数学语言表示出来就是："如果 n 是偶数，那么返回 n 的一半。如果是奇数，就返回 3n+1。"

strange 函数有一个有趣的性质，就是不管最初的输入是什么，把 strange 反复嵌套调用，结果**似乎**总会在某个时候到达 1。也就是说不管 n 是多少，strange(strange...(strange(n))...) 似乎总会在某个深度等于 1。

现在我们写一个函数 checkStrange 来验证这个结论，它的模版是这样：
```js
function checkStrange(start, depth)
{
  // 参数 start 是初始值，depth 用来限制最大深度。
  // 如果在最大深度还没有到 1，就返回 false。
}

show(checkStrange(6243, 10000));  // true
show(checkStrange(237, 10)); // false
show(checkStrange(237, 10000));   // true

// 自己再造一些测试例子
```

## randomCheckStrange
checkStrange 每次只能检查一个输入的情况，但为了验证这个结论，我们想要检查很多的随机输入。现在写一个函数 randomCheckStrange，可以帮助我们反复验证这个结果。只有所有结果都是对的，才返回 true；否则就返回 false，并且打印出第一个不符合条件的输入（用 console.log）。randomCheckStrange 会调用 checkStrange 来完成对单个数字的检查。
```js
function randomCheckStrange(range, depth, count)
{
  // range: 输入的范围
  // depth: 最大深度
  // 检查的次数
}

show(randomCheckStrange(10000, 10, 1000));
// false, 不满足条件: 6000
show(randomCheckStrange(10000, 100, 1000));
// false, 不满足条件: 6595
show(randomCheckStrange(10000, 1000, 1000));
// true
```
**思考**：如果你发现一个"不满足条件的输入"（反例），是否说明之前所说的"一定会到 1"的性质是不成立的？这个时候可以增加允许的递归深度，看看是不是能通过检查。如果你真的找到了对于任何深度都不能到 1 的反例，或者从数学上证明这个性质，那你可能会得一个大奖。

**提示 1**：randomCheckStrange 每次生成一个随机自然数。这可以用 JavaScript 的 Math.random() 函数来实现。不过 Math.random() 会产生一个 [0, 1) 范围内的随机小数。你可以使用 Math.floor(Math.random() * range) + 1 这样的形式来得到你需要的随机自然数。想想为什么？









# 讨论课(四川：先头)

自然数是递归的数据，递归的数据需要递归函数来处理。

**疑问**:老师，之前的base case是一个确定值，即左边==右边，而不是一个范围值，即左边<=右边。当时我没明白这个位置为什么不能是一个范围值。\
**回答**:
```js
function fact(n)
{
    if (n > 0)  //错误写法
    {
        return n * fact(n - 1);
    }
    else //n <= 0
    {
        return 1;
    }
}

function fact(n)
{
    if (n == 0)  //错误写法
    {
        return 1;
    }
    else //为什么else在新的一行? 答：出于人眼考虑,上面的return 1语句和else挨得很近。
    {
        return n * fact(n - 1);
    }
}
```



Yoda notation写法：
```js
if (0 == n) //数字写前面，防止==被写成=。
```

为什么这个表达式(n = 0)等于0呢？因为数学里，y=x=0;

如果一个if...else...中，if语句块是有代码逻辑的，而else是没有任何代码逻辑的。那么是选择不写else语句块还是选择else里面写一个空语句？
**解答**:要尽量少写这种不返回的函数。






# 计算机科学基础班2.0

**【学员：ZhangSuyang】**\
老师，我webstorm已经安装好，应该能正常使用了，但是找不到单行代码调试窗口，所以还没有用它

**【计算机科学家王垠老师ian】**\
不要用单行代码调试工具之类的

**【计算机科学家王垠老师ian】**\
这个课程的代码要靠头脑才能弄明白。之前有个同学每次试图把里面的细节打印出来，结果经常把自己弄糊涂。


**【学员：ZhangSuyang】**\
好的，老师，我试试。。

**【学员：ZhangSuyang】**\
老师：经过摸索，我已经能使用Webstorm调试程序了。

**【计算机科学家王垠老师ian】**\
我之前说了，这个课程建议不要用“调试”这个功能。

**【计算机科学家王垠老师ian】**\
只是能写，能运行就行了。不要用 debug 之类的。

**【学员：ZhangSuyang】**\
老师，是我中文用词不当，其实我用的就是run，就是运行。没有用debug。我把run说成了调试。

**【计算机科学家王垠老师ian】**\
关于在逗号，操作符 + - * / 括号，if 附近加空格的规范大家需要注意一下。这个不只是编程的规范，实际上是通用的英文排版规则，所以对你们写英文也会有帮助的。

**【计算机科学家王垠老师ian】**\
我最近看了点法语，发现法语排版要求在问号，惊叹号前面也加一个空格。这个比英文还要合理些。因为 ! 和 ? 比较长，所以不加空格会和前一个字母挨得太近，不好看。

**【计算机科学家王垠老师ian】**\
Cool!




