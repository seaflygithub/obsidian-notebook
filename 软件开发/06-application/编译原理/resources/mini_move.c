#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <ctype.h>

// --------------------------
// 1. 词法分析（扩大缓冲区，避免溢出）
// --------------------------
typedef enum {
    TOK_EOF,       // 结束符
    TOK_BUFFER,    // "Buffer"关键字
    TOK_MOVE,      // "move"关键字
    TOK_WRITE,     // "write"关键字
    TOK_PRINT,     // "print"关键字
    TOK_IDENTIFIER,// 标识符（变量名）
    TOK_NUMBER,    // 数字（大小）
    TOK_STRING,    // 字符串（"..."）
    TOK_LPAREN,    // (
    TOK_RPAREN,    // )
    TOK_SEMICOLON, // ;
    TOK_EQUALS,    // =
    TOK_DOT        // .
} TokenType;

typedef struct {
    TokenType type;
    char* value;   // 存储内容
    int line;      // 行号（简化）
} Token;

FILE* input_file;
int current_char;

void next_char() {
    current_char = fgetc(input_file);
}

void skip_whitespace() {
    while (current_char != EOF && isspace(current_char)) {
        next_char();
    }
}

// 读取标识符（扩大缓冲区，避免溢出）
Token read_identifier() {
    Token tok = {.type = TOK_IDENTIFIER};
    int len = 0;
    char buf[1024];  // 从128扩大到1024，减少溢出

    while (current_char != EOF && (isalnum(current_char) || current_char == '_') && len < 1023) {
        buf[len++] = current_char;
        next_char();
    }
    buf[len] = '\0';
    tok.value = strdup(buf);  // strdup失败时返回NULL（后续处理）

    if (tok.value) {  // 检查内存分配是否成功
        if (strcmp(tok.value, "Buffer") == 0) tok.type = TOK_BUFFER;
        else if (strcmp(tok.value, "move") == 0) tok.type = TOK_MOVE;
        else if (strcmp(tok.value, "write") == 0) tok.type = TOK_WRITE;
        else if (strcmp(tok.value, "print") == 0) tok.type = TOK_PRINT;
    }
    return tok;
}

// 读取数字（扩大缓冲区）
Token read_number() {
    Token tok = {.type = TOK_NUMBER};
    int len = 0;
    char buf[1024];  // 扩大缓冲区

    while (current_char != EOF && isdigit(current_char) && len < 1023) {
        buf[len++] = current_char;
        next_char();
    }
    buf[len] = '\0';
    tok.value = strdup(buf);
    return tok;
}

// 读取字符串（扩大缓冲区，避免溢出）
Token read_string() {
    Token tok = {.type = TOK_STRING};
    int len = 0;
    char buf[4096];  // 字符串可能较长，进一步扩大

    next_char();  // 跳过开头的"

    while (current_char != EOF && current_char != '"' && len < 4095) {
        buf[len++] = current_char;
        next_char();
    }
    next_char();  // 跳过结尾的"
    buf[len] = '\0';
    tok.value = strdup(buf);
    return tok;
}

// 获取下一个Token（严格处理）
Token get_token() {
    skip_whitespace();
    Token tok = {.type = TOK_EOF, .value = NULL};  // 初始化为EOF

    if (current_char == EOF) return tok;

    switch (current_char) {
        case '(': next_char(); tok.type = TOK_LPAREN; break;
        case ')': next_char(); tok.type = TOK_RPAREN; break;
        case ';': next_char(); tok.type = TOK_SEMICOLON; break;
        case '=': next_char(); tok.type = TOK_EQUALS; break;
        case '.': next_char(); tok.type = TOK_DOT; break;
        case '"': tok = read_string(); break;
        default:
            if (isalpha(current_char)) tok = read_identifier();
            else if (isdigit(current_char)) tok = read_number();
            else next_char();  // 忽略未知字符
    }
    return tok;
}

// --------------------------
// 2. 语法分析（严格检查语法，避免无效节点）
// --------------------------
typedef enum {
    AST_DECLARE, AST_ASSIGN, AST_MOVE, AST_WRITE, AST_PRINT
} ASTNodeType;

typedef struct ASTNode {
    ASTNodeType type;
    char* var_name;
    char* target_name;
    int size;
    char* string_value;
    struct ASTNode* next;
} ASTNode;

ASTNode* create_node(ASTNodeType type) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) {  // 检查内存分配
        fprintf(stderr, "内存分配失败\n");
        exit(1);
    }
    node->type = type;
    node->var_name = node->target_name = node->string_value = NULL;
    node->size = 0;
    node->next = NULL;
    return node;
}

// 安全释放节点（避免内存泄漏）
void free_node(ASTNode* node) {
    if (!node) return;
    free(node->var_name);
    free(node->target_name);
    free(node->string_value);
    free(node);
}

// 解析语句列表（严格检查每个语法步骤）
ASTNode* parse_statements() {
    ASTNode* head = NULL;
    ASTNode** current = &head;
    Token tok = get_token();

    while (tok.type != TOK_EOF) {
        switch (tok.type) {
            case TOK_BUFFER: {
                // 严格解析：Buffer var(size);
                ASTNode* node = create_node(AST_DECLARE);

                // 必须紧跟标识符（变量名）
                tok = get_token();
                if (tok.type != TOK_IDENTIFIER || !tok.value) {
                    free_node(node);
                    tok = get_token();  // 跳过错误token
                    break;
                }
                node->var_name = strdup(tok.value);
                free(tok.value);

                // 必须紧跟 (
                tok = get_token();
                if (tok.type != TOK_LPAREN) {
                    free_node(node);
                    break;
                }

                // 必须紧跟数字（大小）
                tok = get_token();
                if (tok.type != TOK_NUMBER || !tok.value) {
                    free_node(node);
                    break;
                }
                node->size = atoi(tok.value);
                free(tok.value);

                // 必须紧跟 )
                tok = get_token();
                if (tok.type != TOK_RPAREN) {
                    free_node(node);
                    break;
                }

                // 必须紧跟 ;
                tok = get_token();
                if (tok.type != TOK_SEMICOLON) {
                    free_node(node);
                    break;
                }

                // 解析成功，添加到链表
                *current = node;
                current = &node->next;
                break;
            }
            case TOK_IDENTIFIER: {
                if (!tok.value) {  // 检查空指针
                    tok = get_token();
                    break;
                }
                char* var_name = strdup(tok.value);
                free(tok.value);
                tok = get_token();

                if (tok.type == TOK_EQUALS) {
                    // 解析赋值或移动
                    tok = get_token();
                    if (tok.type == TOK_MOVE) {
                        // 移动操作：a = move(b);
                        tok = get_token();  // 必须是 (
                        if (tok.type != TOK_LPAREN) {
                            free(var_name);
                            break;
                        }

                        tok = get_token();  // 必须是标识符（源变量）
                        if (tok.type != TOK_IDENTIFIER || !tok.value) {
                            free(var_name);
                            break;
                        }
                        ASTNode* node = create_node(AST_MOVE);
                        node->var_name = var_name;
                        node->target_name = strdup(tok.value);
                        free(tok.value);

                        tok = get_token();  // 必须是 )
                        if (tok.type != TOK_RPAREN) {
                            free_node(node);
                            break;
                        }

                        tok = get_token();  // 必须是 ;
                        if (tok.type != TOK_SEMICOLON) {
                            free_node(node);
                            break;
                        }

                        *current = node;
                        current = &node->next;
                    } else if (tok.type == TOK_IDENTIFIER && tok.value) {
                        // 普通赋值：a = b;
                        ASTNode* node = create_node(AST_ASSIGN);
                        node->var_name = var_name;
                        node->target_name = strdup(tok.value);
                        free(tok.value);

                        tok = get_token();  // 必须是 ;
                        if (tok.type != TOK_SEMICOLON) {
                            free_node(node);
                            break;
                        }

                        *current = node;
                        current = &node->next;
                    } else {
                        free(var_name);  // 语法错误，释放内存
                    }
                } else if (tok.type == TOK_DOT) {
                    // 解析写入：a.write("...");
                    tok = get_token();  // 必须是 write
                    if (tok.type != TOK_WRITE) {
                        free(var_name);
                        break;
                    }

                    tok = get_token();  // 必须是 (
                    if (tok.type != TOK_LPAREN) {
                        free(var_name);
                        break;
                    }

                    tok = get_token();  // 必须是字符串
                    if (tok.type != TOK_STRING || !tok.value) {
                        free(var_name);
                        break;
                    }
                    ASTNode* node = create_node(AST_WRITE);
                    node->var_name = var_name;
                    node->string_value = strdup(tok.value);
                    free(tok.value);

                    tok = get_token();  // 必须是 )
                    if (tok.type != TOK_RPAREN) {
                        free_node(node);
                        break;
                    }

                    tok = get_token();  // 必须是 ;
                    if (tok.type != TOK_SEMICOLON) {
                        free_node(node);
                        break;
                    }

                    *current = node;
                    current = &node->next;
                } else {
                    free(var_name);  // 语法错误，释放内存
                }
                break;
            }
            case TOK_PRINT: {
                // 解析打印：print(a);
                tok = get_token();  // 必须是 (
                if (tok.type != TOK_LPAREN) {
                    break;
                }

                tok = get_token();  // 必须是标识符
                if (tok.type != TOK_IDENTIFIER || !tok.value) {
                    break;
                }
                ASTNode* node = create_node(AST_PRINT);
                node->var_name = strdup(tok.value);
                free(tok.value);

                tok = get_token();  // 必须是 )
                if (tok.type != TOK_RPAREN) {
                    free_node(node);
                    break;
                }

                tok = get_token();  // 必须是 ;
                if (tok.type != TOK_SEMICOLON) {
                    free_node(node);
                    break;
                }

                *current = node;
                current = &node->next;
                break;
            }
            default:
                // 跳过未知token，避免死循环
                tok = get_token();
                break;
        }
    }
    return head;
}

// --------------------------
// 3. 代码生成（检查空指针）
// --------------------------
void generate_code(ASTNode* ast, FILE* output) {
    if (!output) return;  // 检查输出文件指针

    fprintf(output, "#include <stdio.h>\n", NULL);
    fprintf(output, "#include <stdlib.h>\n", NULL);
    fprintf(output, "#include <string.h>\n\n", NULL);

    // 生成Buffer结构体和工具函数（同前，略）
    fprintf(output, "typedef struct {\n", NULL);
    fprintf(output, "    char* data;\n", NULL);
    fprintf(output, "    size_t size;\n", NULL);
    fprintf(output, "} Buffer;\n\n", NULL);

    fprintf(output, "Buffer buffer_create(size_t size) {\n", NULL);
    fprintf(output, "    Buffer buf = {.data = NULL, .size = 0};\n", NULL);  // 初始化
    fprintf(output, "    if (size > 0) {\n", NULL);
    fprintf(output, "        buf.data = (char*)malloc(size);\n", NULL);
    fprintf(output, "        if (buf.data) {\n", NULL);
    fprintf(output, "            buf.size = size;\n", NULL);
    fprintf(output, "            buf.data[0] = '\\0';\n", NULL);
    fprintf(output, "        }\n", NULL);
    fprintf(output, "    }\n", NULL);
    fprintf(output, "    return buf;\n", NULL);
    fprintf(output, "}\n\n", NULL);

    fprintf(output, "void buffer_destroy(Buffer* buf) {\n", NULL);
    fprintf(output, "    if (buf && buf->data) {\n", NULL);
    fprintf(output, "        free(buf->data);\n", NULL);
    fprintf(output, "        buf->data = NULL;\n", NULL);
    fprintf(output, "        buf->size = 0;\n", NULL);
    fprintf(output, "    }\n", NULL);
    fprintf(output, "}\n\n", NULL);

    fprintf(output, "void buffer_move(Buffer* dest, Buffer* src) {\n", NULL);
    fprintf(output, "    if (!dest || !src) return;\n", NULL);  // 检查空指针
    fprintf(output, "    buffer_destroy(dest);\n", NULL);
    fprintf(output, "    dest->data = src->data;\n", NULL);
    fprintf(output, "    dest->size = src->size;\n", NULL);
    fprintf(output, "    src->data = NULL;\n", NULL);
    fprintf(output, "    src->size = 0;\n", NULL);
    fprintf(output, "}\n\n", NULL);

    fprintf(output, "void buffer_write(Buffer* buf, const char* content) {\n");
    fprintf(output, "    if (!buf || !buf->data || !content) return;\n", NULL);  // 检查
    fprintf(output, "    strncpy(buf->data, content, buf->size - 1);\n", NULL);
    fprintf(output, "    buf->data[buf->size - 1] = '\\0';\n", NULL);
    fprintf(output, "}\n\n", NULL);

    fprintf(output, "void buffer_print(const Buffer* buf, const char* name) {\n", NULL);
    fprintf(output, "    if (!name) return;\n", NULL);  // 检查
    fprintf(output, "    printf(\"%%s: \", name);\n", NULL);
    fprintf(output, "    if (!buf || !buf->data) {\n", NULL);
    fprintf(output, "        printf(\"无资源\\n\");\n", NULL);
    fprintf(output, "    } else {\n", NULL);
    fprintf(output, "        printf(\"数据='%%s', 大小=%%zu\\n\", buf->data, buf->size);\n", NULL);
    fprintf(output, "    }\n", NULL);
    fprintf(output, "}\n\n", NULL);

    fprintf(output, "int main() {\n", NULL);

    // 生成语句（检查节点指针）
    ASTNode* current = ast;
    while (current) {
        if (!current->var_name) {  // 跳过var_name为空的无效节点
            current = current->next;
            continue;
        }

        switch (current->type) {
            case AST_DECLARE:
                fprintf(output, "    Buffer %s = buffer_create(%d);\n",
                        current->var_name, current->size);
                break;
            case AST_ASSIGN:
                if (current->target_name) {  // 检查target_name
                    fprintf(output, "    buffer_destroy(&%s);\n", current->var_name);
                    fprintf(output, "    %s = buffer_create(%s.size);\n",
                            current->var_name, current->target_name);
                    fprintf(output, "    if (%s.data && %s.data) strncpy(%s.data, %s.data, %s.size);\n",
                            current->var_name, current->target_name,
                            current->var_name, current->target_name, current->var_name);
                }
                break;
            case AST_MOVE:
                if (current->target_name) {
                    fprintf(output, "    buffer_move(&%s, &%s);\n",
                            current->var_name, current->target_name);
                }
                break;
            case AST_WRITE:
                if (current->string_value) {
                    fprintf(output, "    buffer_write(&%s, \"%s\");\n",
                            current->var_name, current->string_value);
                }
                break;
            case AST_PRINT:
                fprintf(output, "    buffer_print(&%s, \"%s\");\n",
                        current->var_name, current->var_name);
                break;
        }
        current = current->next;
    }

    // 生成清理代码
    current = ast;
    while (current) {
        if (current->type == AST_DECLARE && current->var_name) {
            fprintf(output, "    buffer_destroy(&%s);\n", current->var_name);
        }
        current = current->next;
    }

    fprintf(output, "    return 0;\n", NULL);
    fprintf(output, "}\n", NULL);
    fflush(output);
}

// --------------------------
// 主函数（完善错误处理）
// --------------------------
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "用法: %s <输入文件.mini> <输出文件.c>\n", argv[0]);
        return 1;
    }

    input_file = fopen(argv[1], "r");
    if (!input_file) {
        perror("无法打开输入文件");
        return 1;
    }

    current_char = fgetc(input_file);
    ASTNode* ast = parse_statements();
    fclose(input_file);

    FILE* output_file = fopen(argv[2], "w+");
    if (!output_file) {
        fprintf(stderr, "无法打开输出文件,%s\n", strerror(errno));
        // 释放AST内存（简化）
        return 1;
    }

    generate_code(ast, output_file);
    fclose(output_file);

    // 释放AST内存（简化版）
    ASTNode* temp;
    while (ast) {
        temp = ast;
        ast = ast->next;
        free_node(temp);
    }

    printf("编译完成：%s -> %s\n", argv[1], argv[2]);
    return 0;
}